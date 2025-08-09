import os
import streamlit as st
from typing import List, Dict
from openai import OpenAI

# Page config
st.set_page_config(page_title="LiaOS – GPT-5/5t Playground", page_icon="🤖", layout="wide")
st.title("🤖 LiaOS – GPT-5/5t Playground (API)")
st.caption("Chat via OpenAI API. Tidak terikat paket ChatGPT UI.")

# API key
API_KEY = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
if not API_KEY:
    st.error("Set `OPENAI_API_KEY` di Streamlit → Settings → Secrets.")
    st.stop()
client = OpenAI(api_key=API_KEY)

# Sidebar (tanpa 4o, tanpa batas manual)
with st.sidebar:
    model_choice = st.radio("Model", ["GPT-5", "GPT-5t"], index=0, horizontal=True)
    model = "gpt-5" if model_choice == "GPT-5" else "gpt-5-turbo"

    gear = st.radio("Gear", ["#lite", "#casual", "#deep", "#full"], index=1, horizontal=True)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.05)
    keep_history = st.checkbox("Pertahankan riwayat", True)

# Prompts by gear (tanpa batas kata)
BASE = "Kamu adalah asisten Lia yang lugas, jelas, empatik, dan adaptif. Jawab natural tanpa jargon."
PROMPTS = {
    "#lite":  BASE + " Jawab ringkas dan langsung ke poin.",
    "#casual":BASE + " Gaya santai namun terstruktur.",
    "#deep":  BASE + " Analisis 2–3 sudut pandang, tetap ringkas.",
    "#full":  BASE + " Full reasoning: Tujuan→Asumsi→Kriteria→Opsi→Risiko→Rekomendasi→Langkah."
}

# State
if "messages" not in st.session_state:
    st.session_state.messages: List[Dict[str, str]] = []
if "last_msgs" not in st.session_state:
    st.session_state.last_msgs = None
if "can_continue" not in st.session_state:
    st.session_state.can_continue = False

# UI
user = st.text_area("Prompt kamu", height=220, placeholder="Tulis di sini…")
col1, col2 = st.columns([1,1])
go = col1.button("Kirim", type="primary")
cont = col2.button("Lanjutkan", disabled=not st.session_state.can_continue)
out_box = st.empty()

def call_chat_stream(mdl: str, msgs: List[Dict[str, str]], temp: float):
    """Streaming; tanpa max_tokens; kembalikan teks & finish_reason."""
    stream = client.chat.completions.create(
        model=mdl, messages=msgs, temperature=temp, stream=True
    )
    full, finish_reason = "", None
    placeholder = out_box.container()
    for chunk in stream:
        choice = chunk.choices[0]
        if getattr(choice.delta, "content", None):
            full += choice.delta.content
            placeholder.markdown(full)
        if choice.finish_reason is not None:
            finish_reason = choice.finish_reason
    return full, finish_reason

def build_msgs(u_text: str) -> List[Dict[str, str]]:
    msgs = st.session_state.messages[:] if keep_history else []
    return [{"role":"system","content":PROMPTS[gear]}, *msgs, {"role":"user","content":f"{gear} {u_text}"}]

# Kirim utama
if go:
    if not user.strip():
        out_box.warning("Tulis prompt terlebih dahulu.")
    else:
        msgs = build_msgs(user)
        with st.spinner("Sedang berpikir…"):
            answer, finish = call_chat_stream(model, msgs, temperature)
        st.session_state.can_continue = (finish == "length")
        st.session_state.last_msgs = msgs + [{"role":"assistant","content":answer}]
        if keep_history:
            st.session_state.messages += [{"role":"user","content":user},{"role":"assistant","content":answer}]

# Lanjutkan jika terpotong
if cont and st.session_state.last_msgs:
    msgs = st.session_state.last_msgs + [{"role":"user","content":"Lanjutkan."}]
    with st.spinner("Melanjutkan…"):
        answer, finish = call_chat_stream(model, msgs, temperature)
    st.session_state.can_continue = (finish == "length")
    st.session_state.last_msgs = msgs + [{"role":"assistant","content":answer}]
    if keep_history:
        st.session_state.messages += [{"role":"user","content":"Lanjutkan."},{"role":"assistant","content":answer}]
