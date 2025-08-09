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

# Sidebar (tanpa 4o)
with st.sidebar:
    model_choice = st.radio("Model", ["GPT-5", "GPT-5t"], index=0, horizontal=True)
    model = "gpt-5" if model_choice == "GPT-5" else "gpt-5-turbo"

    gear = st.radio("Gear", ["#lite", "#casual", "#deep", "#full"], index=1, horizontal=True)

    # Preset: (temperature, max_tokens) — long form defaults
    PRESETS = {"#lite": (0.3, 2000), "#casual": (0.7, 3000), "#deep": (0.5, 3500), "#full": (0.4, 4000)}
    t_default, mt_default = PRESETS[gear]
    temperature = st.slider("Temperature", 0.0, 1.0, t_default, 0.05)
    max_tokens = st.slider("Max tokens (output)", 256, 4000, mt_default, 64)
    keep_history = st.checkbox("Pertahankan riwayat", True)

# Prompts by gear (tanpa batas kata)
BASE = "Kamu adalah asisten Lia yang lugas, jelas, empatik, dan adaptif. Jawab natural tanpa jargon."
PROMPTS = {
    "#lite": BASE + " Jawab ringkas dan langsung ke poin.",
    "#casual": BASE + " Gaya santai namun terstruktur.",
    "#deep": BASE + " Analisis 2–3 sudut pandang, tetap ringkas.",
    "#full": BASE + " Full reasoning: Tujuan→Asumsi→Kriteria→Opsi→Risiko→Rekomendasi→Langkah."
}

# State
if "messages" not in st.session_state:
    st.session_state.messages: List[Dict[str, str]] = []

# UI
user = st.text_area("Prompt kamu", height=200, placeholder="Tulis di sini…")
go = st.button("Kirim", type="primary")
out_box = st.empty()

def call_chat(mdl: str, msgs: List[Dict[str, str]], temp: float, mx: int) -> str:
    resp = client.chat.completions.create(model=mdl, messages=msgs, temperature=temp, max_tokens=mx)
    return resp.choices[0].message.content

if go:
    if not user.strip():
        out_box.warning("Tulis prompt terlebih dahulu.")
    else:
        msgs = st.session_state.messages[:] if keep_history else []
        msgs = [{"role": "system", "content": PROMPTS[gear]}, *msgs, {"role": "user", "content": f"{gear} {user}"}]
        with st.spinner("Sedang berpikir…"):
            answer = call_chat(model, msgs, temperature, max_tokens)
        out_box.markdown(answer)
        if keep_history:
            st.session_state.messages += [
                {"role": "user", "content": user},
                {"role": "assistant", "content": answer},
            ]
