"""AI Content Writer — powered by Qwen2.5-0.5B-Instruct."""

import streamlit as st
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Content Writer",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Constants ──────────────────────────────────────────────────────────────────
MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"

CONTENT_TYPES = [
    "Blog Post", "Article", "Essay",
    "Social Media Post", "Product Description", "Marketing Copy",
]
TONES = [
    "Professional", "Friendly", "Informative",
    "Persuasive", "Creative", "Casual",
]
LENGTHS = {
    "Short  (~150 words)": 150,
    "Medium (~300 words)": 300,
    "Long   (~500 words)": 500,
}

# ── Model loading — cached, loads only once ────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_model():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, use_fast=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        device_map="cpu",
        torch_dtype=torch.float32,
        low_cpu_mem_usage=True,
    )
    model.eval()
    return model, tokenizer

# ── Sidebar — settings ─────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Settings")

    content_type = st.selectbox("Content Type", CONTENT_TYPES)
    tone         = st.selectbox("Tone", TONES)
    length_label = st.selectbox("Length", list(LENGTHS.keys()), index=1)
    max_tokens   = LENGTHS[length_label]

    st.divider()

    temperature = st.slider(
        "Temperature",
        min_value=0.1, max_value=1.2,
        value=0.7, step=0.1,
        help="Low = focused & consistent · High = creative & varied",
    )
    st.caption("🎯 Focused" if temperature < 0.5 else "⚖️ Balanced" if temperature < 0.9 else "🎨 Creative")

    st.divider()

    st.subheader("🤖 Model")
    st.caption("Model loads on first generation. Click to pre-load.")
    if st.button("Pre-load Model", use_container_width=True):
        with st.spinner("Downloading Qwen2.5-0.5B… first time ~1–2 min"):
            load_model()
        st.success("✅ Model ready!")

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("✍️ AI Content Writer")
st.caption("Generate professional blogs, articles, social posts & more — powered by Qwen2.5-0.5B-Instruct.")

st.divider()

# ── Two-column layout ──────────────────────────────────────────────────────────
left, right = st.columns(2, gap="large")

with left:
    st.subheader("📋 Your Topic")

    topic = st.text_area(
        "Enter your topic",
        placeholder="e.g. The future of artificial intelligence in healthcare…",
        height=150,
        label_visibility="collapsed",
    )

    if topic.strip():
        short_len = length_label.split("(")[0].strip()
        st.info(f"📌 **{content_type}** · **{tone}** tone · **{short_len}**")

    clicked = st.button("🚀 Generate Content", type="primary", use_container_width=True)

with right:
    st.subheader("📄 Generated Content")

    if clicked:
        if not topic.strip():
            st.error("⚠️ Please enter a topic first.")
        elif len(topic.strip()) < 2:
            st.error("⚠️ Topic too short — at least 2 characters.")
        else:
            with st.spinner("✍️ Writing your content… (first run loads the model ~1–2 min)"):
                try:
                    model, tokenizer = load_model()

                    prompt = (
                        f"Write a {content_type.lower()} on the topic \"{topic.strip()}\". "
                        f"Tone: {tone}. "
                        f"Length: approximately {length_label.split('(')[0].strip().lower()} "
                        f"({max_tokens} tokens). "
                        f"Return only the content, no explanations or headings."
                    )

                    input_ids = tokenizer(prompt, return_tensors="pt").input_ids

                    with torch.no_grad():
                        output = model.generate(
                            input_ids,
                            max_new_tokens=max_tokens,
                            temperature=temperature,
                            do_sample=True,
                            pad_token_id=tokenizer.eos_token_id,
                        )

                    result = tokenizer.decode(
                        output[0][input_ids.shape[-1]:],
                        skip_special_tokens=True,
                    ).strip()

                    if result:
                        st.session_state.content = result
                        st.session_state.topic   = topic.strip()
                    else:
                        st.warning("Model returned empty output — try again.")

                except Exception as exc:
                    st.error(f"❌ Generation failed: {exc}")

    if "content" in st.session_state:
        content = st.session_state.content

        st.text_area(
            "output",
            value=content,
            height=320,
            label_visibility="collapsed",
        )

        st.caption(f"📊 {len(content.split())} words · {len(content)} characters")

        c1, c2 = st.columns(2)
        with c1:
            fname = f"{st.session_state.get('topic', 'content')[:40]}.txt"
            st.download_button(
                "⬇️ Download .txt",
                data=content,
                file_name=fname,
                mime="text/plain",
                use_container_width=True,
            )
        with c2:
            if st.button("🔄 Clear", use_container_width=True):
                del st.session_state.content
                del st.session_state.topic
                st.rerun()

    elif not clicked:
        st.info("Enter a topic on the left and click **Generate Content**.")
