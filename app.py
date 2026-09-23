"""AI Content Writer — Streamlit Cloud app powered by Qwen2.5-0.5B-Instruct."""

import streamlit as st
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# ── Page config (must be first Streamlit call) ─────────────────────────────────
st.set_page_config(
    page_title="AI Content Writer",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header  { visibility: hidden; }

/* Hero */
.hero {
    background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    color: white;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: "";
    position: absolute;
    top: -50px; right: -50px;
    width: 220px; height: 220px;
    background: rgba(255,255,255,0.07);
    border-radius: 50%;
}
.hero::after {
    content: "";
    position: absolute;
    bottom: -60px; left: -20px;
    width: 200px; height: 200px;
    background: rgba(255,255,255,0.05);
    border-radius: 50%;
}
.hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.2);
    border-radius: 999px;
    padding: 4px 14px;
    font-size: 0.78rem;
    font-weight: 500;
    margin-bottom: 0.75rem;
}
.hero h1 { font-size: 1.9rem; font-weight: 700; margin: 0 0 0.35rem; }
.hero p  { font-size: 0.92rem; opacity: 0.85; margin: 0; max-width: 480px; }

/* Stat cards */
.stats {
    display: flex;
    gap: 0.85rem;
    margin-bottom: 1.8rem;
    flex-wrap: wrap;
}
.stat {
    flex: 1; min-width: 130px;
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 0.9rem 1.1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.stat-icon  { font-size: 1.3rem; margin-bottom: 0.3rem; }
.stat-label { font-size: 0.72rem; color: #6b7280; font-weight: 500; text-transform: uppercase; letter-spacing: .04em; }
.stat-value { font-size: 1.05rem; font-weight: 700; color: #111827; }

/* Output box */
.output-box {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-left: 4px solid #2563eb;
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    white-space: pre-wrap;
    font-size: 0.91rem;
    line-height: 1.8;
    color: #1e293b;
    max-height: 440px;
    overflow-y: auto;
}

/* Summary pill */
.summary-pill {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 8px;
    padding: 0.55rem 0.9rem;
    font-size: 0.82rem;
    color: #1d4ed8;
    margin-bottom: 0.8rem;
}

/* Sidebar labels */
.sidebar-heading {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .06em;
    color: #6b7280;
    margin: 1rem 0 0.2rem;
}

/* Generate button */
div.stButton > button {
    background: linear-gradient(135deg, #2563eb, #4f46e5);
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.65rem 1.5rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    width: 100% !important;
    transition: opacity .2s;
}
div.stButton > button:hover { opacity: 0.87; }

/* Sidebar bg */
section[data-testid="stSidebar"] { background: #f8fafc; }
</style>
""", unsafe_allow_html=True)

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

# ── Model — cached so it loads only once per session ──────────────────────────
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

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">✨ Powered by Qwen2.5-0.5B-Instruct</div>
    <h1>✍️ AI Content Writer</h1>
    <p>Generate professional blogs, articles, social posts & more — instantly and for free.</p>
</div>
""", unsafe_allow_html=True)

# ── Stat cards ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="stats">
  <div class="stat"><div class="stat-icon">📝</div><div class="stat-label">Content Types</div><div class="stat-value">6</div></div>
  <div class="stat"><div class="stat-icon">🎨</div><div class="stat-label">Tones</div><div class="stat-value">6</div></div>
  <div class="stat"><div class="stat-icon">⚡</div><div class="stat-label">Model Size</div><div class="stat-value">0.5B</div></div>
  <div class="stat"><div class="stat-icon">🆓</div><div class="stat-label">Cost</div><div class="stat-value">Free</div></div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")

    st.markdown('<p class="sidebar-heading">Content</p>', unsafe_allow_html=True)
    content_type = st.selectbox("Content Type", CONTENT_TYPES)
    tone         = st.selectbox("Tone", TONES)
    length_label = st.selectbox("Length", list(LENGTHS.keys()), index=1)
    max_tokens   = LENGTHS[length_label]

    st.markdown('<p class="sidebar-heading">Creativity</p>', unsafe_allow_html=True)
    temperature = st.slider("Temperature", 0.1, 1.2, 0.7, 0.1,
                            help="Low = focused & consistent · High = creative & varied")
    st.caption("🎯 Focused" if temperature < 0.5 else "⚖️ Balanced" if temperature < 0.9 else "🎨 Creative")

    st.divider()
    st.markdown("### 🤖 Model")
    st.caption("Model loads automatically on first generation. Click below to pre-load.")
    if st.button("Pre-load Model", use_container_width=True):
        with st.spinner("Downloading Qwen2.5-0.5B… first time ~1–2 min"):
            load_model()
        st.success("✅ Model ready!")

# ── Main layout ────────────────────────────────────────────────────────────────
left, right = st.columns([1, 1], gap="large")

with left:
    st.markdown("### 📋 Your Topic")
    topic = st.text_area(
        "topic_input",
        placeholder="e.g. The future of artificial intelligence in healthcare…",
        height=150,
        label_visibility="collapsed",
    )

    if topic.strip():
        short_len = length_label.split("(")[0].strip()
        st.markdown(
            f'<div class="summary-pill">📌 <b>{content_type}</b> &nbsp;·&nbsp; '
            f'<b>{tone}</b> tone &nbsp;·&nbsp; <b>{short_len}</b></div>',
            unsafe_allow_html=True,
        )

    clicked = st.button("🚀 Generate Content", use_container_width=True)

with right:
    st.markdown("### 📄 Generated Content")

    if clicked:
        if not topic.strip():
            st.error("⚠️ Please enter a topic first.")
        elif len(topic.strip()) < 2:
            st.error("⚠️ Topic too short — enter at least 2 characters.")
        else:
            with st.spinner("✍️ Writing your content… (first run loads the model — may take 1–2 min)"):
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

        st.markdown(
            f'<div class="output-box">{content}</div>',
            unsafe_allow_html=True,
        )

        words = len(content.split())
        st.caption(f"📊 {words} words · {len(content)} characters")

        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            fname = f"{st.session_state.get('topic','content')[:30]}.txt"
            st.download_button("⬇️ Download .txt", content,
                               file_name=fname, mime="text/plain",
                               use_container_width=True)
        with c2:
            if st.button("🔄 Clear", use_container_width=True):
                del st.session_state.content
                del st.session_state.topic
                st.rerun()

    elif not clicked:
        st.markdown("""
        <div style="text-align:center;padding:3.5rem 1rem;color:#94a3b8;">
            <div style="font-size:3.5rem">✍️</div>
            <p style="margin-top:.6rem;font-size:.9rem">
                Choose your settings in the sidebar,<br>enter a topic, and hit <b>Generate</b>.
            </p>
        </div>
        """, unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<p style='text-align:center;color:#94a3b8;font-size:.78rem;'>"
    "AI Content Writer &nbsp;·&nbsp; Qwen2.5-0.5B-Instruct &nbsp;·&nbsp; "
    "Built with Streamlit &nbsp;·&nbsp; "
    "<a href='https://streamlit.io/cloud' style='color:#94a3b8;'>Streamlit Cloud</a>"
    "</p>",
    unsafe_allow_html=True,
)
