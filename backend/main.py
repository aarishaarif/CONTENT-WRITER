"""FastAPI backend for the AI Content Writer app."""

import os
import threading
from typing import Literal

import torch
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from transformers import AutoModelForCausalLM, AutoTokenizer

CONTENT_TYPES = Literal["blog post", "article", "essay", "social media post", "product description", "marketing copy"]
TONES = Literal["Professional", "Friendly", "Informative", "Persuasive", "Creative", "Casual"]
LENGTHS = {"Short": 150, "Medium": 300, "Long": 500}


class GenerateRequest(BaseModel):
    topic: str = Field(min_length=2, max_length=500)
    content_type: CONTENT_TYPES
    tone: TONES
    length: Literal["Short", "Medium", "Long"]
    temperature: float = Field(default=0.7, ge=0.1, le=1.2)


class GenerateResponse(BaseModel):
    content: str


app = FastAPI(title="AI Content Writer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_model: AutoModelForCausalLM | None = None
_tokenizer: AutoTokenizer | None = None
_model_lock = threading.Lock()
_model_loaded = False


def load_model() -> tuple[AutoModelForCausalLM, AutoTokenizer]:
    """Load the Qwen model once at startup."""
    global _model, _tokenizer, _model_loaded
    if _model_loaded:
        return _model, _tokenizer

    with _model_lock:
        if _model_loaded:
            return _model, _tokenizer

        device = "cuda" if torch.cuda.is_available() else "cpu"
        model_id = "Qwen/Qwen2.5-0.5B-Instruct"

        try:
            _tokenizer = AutoTokenizer.from_pretrained(model_id, use_fast=True)
            _model = AutoModelForCausalLM.from_pretrained(
                model_id,
                device_map=device,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            )
            _model.eval()
            _model_loaded = True
            print(f"Model loaded on {device}")
        except Exception as exc:
            raise RuntimeError(f"Failed to load model: {exc}") from exc

    return _model, _tokenizer


@app.on_event("startup")
def startup() -> None:
    """Load the model once when the server starts."""
    load_model()


@app.get("/health")
def health() -> dict[str, str | bool]:
    """Check server uptime and model readiness."""
    return {"status": "ok", "model_loaded": _model_loaded}


@app.post("/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest) -> GenerateResponse:
    """Generate content based on the request parameters."""
    global _model, _tokenizer

    if _model is None or _tokenizer is None:
        raise HTTPException(status_code=503, detail="Model is still loading")

    max_length = LENGTHS[request.length]
    prompt = (
        f"Write a {request.content_type} on the topic \"{request.topic}\". "
        f"Tone: {request.tone}. Length: approximately {request.length.lower()} "
        f"({max_length} tokens). Return only the content, no explanations."
    )

    try:
        input_ids = _tokenizer(prompt, return_tensors="pt").input_ids
        device = next(_model.parameters()).device
        input_ids = input_ids.to(device)

        with torch.no_grad():
            output = _model.generate(
                input_ids,
                max_new_tokens=max_length,
                temperature=request.temperature,
                do_sample=True,
                pad_token_id=_tokenizer.eos_token_id,
            )

        content = _tokenizer.decode(output[0][input_ids.shape[-1]:], skip_special_tokens=True).strip()
        return GenerateResponse(content=content or "No content was generated.")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Generation failed: {exc}") from exc
