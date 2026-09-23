"""Tests for the AI Content Writer FastAPI backend.

The Qwen model (and torch) are fully mocked so CI can run these tests
without downloading 500 MB of model weights or installing GPU libraries.
All business logic, request validation, and response shapes are tested.
"""

import sys
import types
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Mock heavy dependencies BEFORE main.py is imported
# ---------------------------------------------------------------------------

def _make_fake_torch():
    """Return a minimal torch mock that satisfies main.py's usage."""
    torch_mock = MagicMock(name="torch")

    # torch.cuda.is_available() -> False
    torch_mock.cuda.is_available.return_value = False

    # torch.float16, torch.float32 — just sentinel strings are fine
    torch_mock.float16 = "float16"
    torch_mock.float32 = "float32"

    # torch.no_grad() used as a context manager
    torch_mock.no_grad.return_value.__enter__ = lambda s: None
    torch_mock.no_grad.return_value.__exit__ = MagicMock(return_value=False)

    return torch_mock


def _make_fake_transformers():
    """Return a minimal transformers mock."""
    transformers_mock = MagicMock(name="transformers")
    return transformers_mock


# Inject fakes into sys.modules before any import of main
_torch_mock = _make_fake_torch()
_transformers_mock = _make_fake_transformers()

sys.modules.setdefault("torch", _torch_mock)
sys.modules.setdefault("transformers", _transformers_mock)
sys.modules.setdefault("accelerate", MagicMock(name="accelerate"))


# ---------------------------------------------------------------------------
# Build the fake model / tokenizer used across all tests
# ---------------------------------------------------------------------------

def _make_fake_model_and_tokenizer():
    fake_tokenizer = MagicMock(name="tokenizer")
    fake_tokenizer.eos_token_id = 0

    # tokenizer(prompt, return_tensors="pt").input_ids
    # needs: .to(device) -> input_ids, .shape[-1] -> int
    fake_ids = MagicMock(name="input_ids")
    fake_ids.to.return_value = fake_ids   # ids.to(device) returns itself
    fake_ids.shape = [1, 5]              # shape[-1] == 5

    fake_tokenizer.return_value.input_ids = fake_ids

    # output[0][5:] — output is a MagicMock; output[0] is also a MagicMock;
    # output[0][5:] is also a MagicMock; decode() just returns a string
    fake_tokenizer.decode.return_value = "Mocked generated content."

    fake_model = MagicMock(name="model")
    param = MagicMock()
    param.device = "cpu"
    # parameters() must return a fresh iterator each time it's called
    fake_model.parameters.side_effect = lambda: iter([param])
    # generate() return value — indexing via __getitem__ falls through to MagicMock
    fake_model.generate.return_value = MagicMock(name="output_tensor")

    return fake_model, fake_tokenizer


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def client():
    fake_model, fake_tokenizer = _make_fake_model_and_tokenizer()

    with patch.dict(sys.modules, {"torch": _torch_mock, "transformers": _transformers_mock}), \
         patch("main.load_model", return_value=(fake_model, fake_tokenizer)), \
         patch("main._model", fake_model), \
         patch("main._tokenizer", fake_tokenizer), \
         patch("main._model_loaded", True):
        from fastapi.testclient import TestClient
        from main import app
        yield TestClient(app)


# ---------------------------------------------------------------------------
# /health
# ---------------------------------------------------------------------------

class TestHealth:
    def test_returns_200(self, client):
        assert client.get("/health").status_code == 200

    def test_response_has_status_key(self, client):
        assert "status" in client.get("/health").json()

    def test_status_is_ok(self, client):
        assert client.get("/health").json()["status"] == "ok"

    def test_response_has_model_loaded_key(self, client):
        assert "model_loaded" in client.get("/health").json()


# ---------------------------------------------------------------------------
# /generate — happy path
# ---------------------------------------------------------------------------

VALID_PAYLOAD = {
    "topic": "machine learning",
    "content_type": "blog post",
    "tone": "Informative",
    "length": "Medium",
    "temperature": 0.7,
}


class TestGenerate:
    def test_returns_200_for_valid_request(self, client):
        assert client.post("/generate", json=VALID_PAYLOAD).status_code == 200

    def test_response_has_content_key(self, client):
        assert "content" in client.post("/generate", json=VALID_PAYLOAD).json()

    def test_content_is_string(self, client):
        data = client.post("/generate", json=VALID_PAYLOAD).json()
        assert isinstance(data["content"], str)

    def test_all_content_types_accepted(self, client):
        for ct in ["blog post", "article", "essay",
                   "social media post", "product description", "marketing copy"]:
            r = client.post("/generate", json={**VALID_PAYLOAD, "content_type": ct})
            assert r.status_code == 200, f"content_type={ct!r} → {r.status_code}"

    def test_all_tones_accepted(self, client):
        for tone in ["Professional", "Friendly", "Informative",
                     "Persuasive", "Creative", "Casual"]:
            r = client.post("/generate", json={**VALID_PAYLOAD, "tone": tone})
            assert r.status_code == 200, f"tone={tone!r} → {r.status_code}"

    def test_all_lengths_accepted(self, client):
        for length in ("Short", "Medium", "Long"):
            r = client.post("/generate", json={**VALID_PAYLOAD, "length": length})
            assert r.status_code == 200, f"length={length!r} → {r.status_code}"

    def test_temperature_boundaries(self, client):
        for temp in (0.1, 0.7, 1.2):
            r = client.post("/generate", json={**VALID_PAYLOAD, "temperature": temp})
            assert r.status_code == 200, f"temperature={temp} → {r.status_code}"


# ---------------------------------------------------------------------------
# /generate — validation errors (422 Unprocessable Entity)
# ---------------------------------------------------------------------------

class TestGenerateValidation:
    def test_missing_topic_returns_422(self, client):
        payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "topic"}
        assert client.post("/generate", json=payload).status_code == 422

    def test_topic_too_short_returns_422(self, client):
        assert client.post("/generate", json={**VALID_PAYLOAD, "topic": "x"}).status_code == 422

    def test_topic_too_long_returns_422(self, client):
        assert client.post("/generate", json={**VALID_PAYLOAD, "topic": "a" * 501}).status_code == 422

    def test_invalid_content_type_returns_422(self, client):
        assert client.post("/generate", json={**VALID_PAYLOAD, "content_type": "tweet"}).status_code == 422

    def test_invalid_tone_returns_422(self, client):
        assert client.post("/generate", json={**VALID_PAYLOAD, "tone": "Aggressive"}).status_code == 422

    def test_invalid_length_returns_422(self, client):
        assert client.post("/generate", json={**VALID_PAYLOAD, "length": "XL"}).status_code == 422

    def test_temperature_too_low_returns_422(self, client):
        assert client.post("/generate", json={**VALID_PAYLOAD, "temperature": 0.0}).status_code == 422

    def test_temperature_too_high_returns_422(self, client):
        assert client.post("/generate", json={**VALID_PAYLOAD, "temperature": 1.3}).status_code == 422

    def test_empty_body_returns_422(self, client):
        assert client.post("/generate", json={}).status_code == 422
