import streamlit as st import os from openai import OpenAI from typing import List, Dict

------------------------------

Page config

------------------------------

st.set_page_config( page_title="LiaOS – GPT-5/5t Playground", page_icon="🤖", layout="wide", )

st.title("🤖 LiaOS – GPT-5/5t Playground (API)") st.caption( "Chat pribadi via OpenAI API. Billing pakai API Key kamu, tidak terikat paket ChatGPT UI." )

------------------------------

Secrets / API Key

------------------------------

API_KEY = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY")) if not API_KEY: with st.sidebar: st.error( "API key tidak ditemukan. Tambahkan di Settings → Secrets dengan kunci OPENAI_API_KEY." ) st.code('''# Streamlit Secrets (contoh) OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxx"''', language="bash") st.stop()

client = OpenAI(api_key=API_KEY)

------------------------------

Sidebar Controls

------------------------------

with st.sidebar: st.subheader("⚙️ Pengaturan")

# Model switch (G5 ↔︎ G5t)
model_choice = st.radio(
    "Model",
    options=["GPT-5", "GPT-5t"],
    index=0,
    horizontal=True,
    help="Pilih GPT-5 untuk kualitas stabil; GPT-5t untuk reasoning/turbo.",
)
model = "gpt-5" if model_choice == "GPT-5" else "gpt-5-turbo"
    ],
    index=1,
    help=(
        "gpt-4o: cepat & ekonomis | "
        "gpt-5: kualitas tinggi | "
        "gpt-5-turbo: reasoning lebih dalam"
    ),
)

gear = st.radio(
    "Gear (gaya respons)",
    options=["#lite", "#casual", "#deep", "#full"],
    index=1,
    help=(
        "#lite: singkat | #casual: normal | "
        "#deep: analisis ringkas | #full: full reasoning"
    ),
    horizontal=True,
)

# Preset by gear – can be overridden below
def gear_presets(g: str):
    if g == "#lite":
        return dict(temp=0.3, max_new_tokens=600)
    if g == "#deep":
        return dict(temp=0.5, max_new_tokens=1400)
    if g == "#full":
        return dict(temp=0.4, max_new_tokens=2200)
    # #casual
    return dict(temp=0.7, max_new_tokens=1000)

presets = gear_presets(gear)

temperature = st.slider("Temperature", 0.0, 1.0, presets["temp"], 0.05)
max_tokens = st.slider("Max tokens (jawaban)", 256, 4000, presets["max_new_tokens"], 64)

keep_history = st.checkbox("Pertahankan riwayat percakapan", value=True)

st.divider()
with st.expander("ℹ️ Petunjuk cepat"):
    st.markdown(
        "- Simpan API key di **Secrets** (bukan di kode).\n"
        "- Gunakan *gear* untuk mengendalikan gaya jawaban.\n"
        "- Model bisa diubah kapan saja.\n"
        "- Billing: pay-as-you-go via API key."
    )

------------------------------

Session State for Chat

------------------------------

if "messages" not in st.session_state: st.session_state.messages: List[Dict[str, str]] = []

------------------------------

System Prompt by Gear

------------------------------

BASE_IDENTITY = ( "Kamu adalah asisten Lia yang lugas, jelas, empatik, dan adaptif. " "Jawab dalam bahasa yang natural, hindari jargon berlebihan kecuali diminta." )

PROMPTS_BY_GEAR = { "#lite": ( BASE_IDENTITY + " Fokus ke inti, maksimal ~120 kata. Beri poin bullet seperlunya. Jangan overthinking." ), "#casual": ( BASE_IDENTITY + " Gaya percakapan santai namun terstruktur. Jelas, padat, tidak terlalu panjang." ), "#deep": ( BASE_IDENTITY + " Beri analisis 2–3 sudut pandang, tetap ringkas. Gunakan subjudul singkat & bullet penting." ), "#full": ( BASE_IDENTITY + ( " Gunakan gaya 'full reasoning' terstruktur: Tujuan & konteks → Asumsi/batasan → " "Kriteria evaluasi → Opsi & perbandingan → Risiko/unknowns → Rekomendasi → Langkah berikutnya. " "Tulis rapi dengan heading singkat." ) ), }

------------------------------

UI – Chat Box

------------------------------

col_in, col_out = st.columns([1, 1.2])

with col_in: user_input = st.text_area("Prompt kamu", height=200, placeholder="Tulis di sini…") send = st.button("Kirim", type="primary")

with col_out: st.markdown("### 💬 Output") output_area = st.empty()

------------------------------

Helper: call OpenAI Chat API (with optional streaming)

------------------------------

def call_openai_chat(model_name: str, messages: List[Dict[str, str]], temperature: float, max_tokens: int): """Call Chat Completions API with basic streaming to the UI.""" try: stream = client.chat.completions.create( model=model_name, messages=messages, temperature=temperature, max_tokens=max_tokens, stream=True, ) full_text = "" placeholder = output_area.container() for chunk in stream: delta = chunk.choices[0].delta if getattr(delta, "content", None): full_text += delta.content placeholder.markdown(full_text) return full_text except Exception as e: output_area.error(f"Kesalahan API: {e}") return None

------------------------------

Run

------------------------------

if send: if not user_input or not user_input.strip(): output_area.warning("Tulis prompt terlebih dahulu.") else: # Build message list messages: List[Dict[str, str]] = [] if keep_history and st.session_state.messages: messages.extend(st.session_state.messages)

# Inject system prompt based on gear
    messages = [
        {"role": "system", "content": PROMPTS_BY_GEAR.get(gear, PROMPTS_BY_GEAR["#casual"])},
        *messages,
        {"role": "user", "content": f"{gear} {user_input}"},
    ]

    # Call API
    with st.spinner("Sedang berpikir…"):
        answer = call_openai_chat(
            model_name=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    # Update history
    if answer:
        if keep_history:
            st.session_state.messages.extend(
                [
                    {"role": "user", "content": user_input},
                    {"role": "assistant", "content": answer},
                ]
            )

------------------------------

History management

------------------------------

st.divider() with st.expander("🧹 Riwayat Percakapan"): if st.button("Clear history"): st.session_state.messages = [] st.success("Riwayat dibersihkan.") if st.session_state.messages: st.write(st.session_state.messages)

------------------------------

Footer helper (requirements)

------------------------------

with st.expander("📦 requirements.txt (yang diperlukan)"): st.code(""" streamlit openai """, language="bash")

