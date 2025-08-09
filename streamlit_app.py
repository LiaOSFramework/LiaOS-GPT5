import streamlit as st import os from openai import OpenAI from typing import List, Dict

st.set_page_config( page_title="LiaOS – GPT-5/5t Playground", page_icon="🤖", layout="wide", )

st.title("🤖 LiaOS – GPT-5/5t Playground (API)") st.caption("Chat pribadi via OpenAI API. Billing pakai API Key kamu, tidak terikat paket ChatGPT UI.")

API_KEY = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY")) if not API_KEY: st.error("API key tidak ditemukan. Tambahkan di Settings → Secrets dengan kunci OPENAI_API_KEY.") st.stop()

client = OpenAI(api_key=API_KEY)

with st.sidebar: st.subheader("⚙️ Pengaturan") model_choice = st.radio( "Model", options=["GPT-5", "GPT-5t"], index=0, horizontal=True, help="Pilih GPT-5 untuk kualitas stabil; GPT-5t untuk reasoning/turbo." ) model = "gpt-5" if model_choice == "GPT-5" else "gpt-5-turbo"

gear = st.radio(
    "Gear (gaya respons)",
    options=["#lite", "#casual", "#deep", "#full"],
    index=1,
    help="#lite: singkat | #casual: normal | #deep: analisis ringkas | #full: full reasoning",
    horizontal=True,
)

def gear_presets(g: str):
    if g == "#lite":
        return dict(temp=0.3, max_new_tokens=600)
    if g == "#deep":
        return dict(temp=0.5, max_new_tokens=1400)
    if g == "#full":
        return dict(temp=0.4, max_new_tokens=2200)
    return dict(temp=0.7, max_new_tokens=1000)

presets = gear_presets(gear)
temperature = st.slider("Temperature", 0.0, 1.0, presets["temp"], 0.05)
max_tokens = st.slider("Max tokens (jawaban)", 256, 4000, presets["max_new_tokens"], 64)
keep_history = st.checkbox("Pertahankan riwayat percakapan", value=True)

if "messages" not in st.session_state: st.session_state.messages: List[Dict[str, str]] = []

BASE_IDENTITY = ( "Kamu adalah asisten Lia yang lugas, jelas, empatik, dan adaptif. " "Jawab dalam bahasa yang natural, hindari jargon berlebihan kecuali diminta." )

PROMPTS_BY_GEAR = { "#lite": BASE_IDENTITY + " Fokus ke inti, maksimal ~120 kata.", "#casual": BASE_IDENTITY + " Gaya percakapan santai namun terstruktur.", "#deep": BASE_IDENTITY + " Beri analisis 2–3 sudut pandang, tetap ringkas.", "#full": BASE_IDENTITY + " Gunakan gaya 'full reasoning' terstruktur.", }

user_input = st.text_area("Prompt kamu", height=200) send = st.button("Kirim", type="primary") output_area = st.empty()

def call_openai_chat(model_name: str, messages: List[Dict[str, str]], temperature: float, max_tokens: int): try: response = client.chat.completions.create( model=model_name, messages=messages, temperature=temperature, max_tokens=max_tokens ) return response.choices[0].message.content except Exception as e: output_area.error(f"Kesalahan API: {e}") return None

if send: if not user_input.strip(): output_area.warning("Tulis prompt terlebih dahulu.") else: messages: List[Dict[str, str]] = [] if keep_history and st.session_state.messages: messages.extend(st.session_state.messages) messages = [ {"role": "system", "content": PROMPTS_BY_GEAR.get(gear, PROMPTS_BY_GEAR["#casual"])}, *messages, {"role": "user", "content": f"{gear} {user_input}"}, ] with st.spinner("Sedang berpikir…"): answer = call_openai_chat( model_name=model, messages=messages, temperature=temperature, max_tokens=max_tokens, ) if answer: output_area.markdown(answer) if keep_history: st.session_state.messages.extend( [ {"role": "user", "content": user_input}, {"role": "assistant", "content": answer}, ] )

with st.expander("🧹 Riwayat Percakapan"): if st.button("Clear history"): st.session_state.messages = [] st.success("Riwayat dibersihkan.") if st.session_state.messages: st.write(st.session_state.messages)

with st.expander("📦 requirements.txt"): st.code(""" streamlit openai """, language="bash")

