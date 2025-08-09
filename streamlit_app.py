import streamlit as st
from openai import OpenAI
import os

# Ambil API key dari environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    st.error("API key tidak ditemukan. Set variabel lingkungan OPENAI_API_KEY terlebih dahulu.")
    st.stop()

# Inisialisasi client OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Konfigurasi halaman
st.set_page_config(page_title="GPT-5 Playground", page_icon="🤖", layout="wide")
st.title("🤖 GPT-5 Playground")
st.write("Chat langsung dengan GPT-5 lewat API OpenAI.")

# Input user
user_input = st.text_area("Tulis prompt kamu di sini:", height=150)

# Tombol kirim
if st.button("Kirim ke GPT-5"):
    if user_input.strip() == "":
        st.warning("Masukkan prompt terlebih dahulu.")
    else:
        with st.spinner("Sedang berpikir..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-5",
                    messages=[
                        {"role": "system", "content": "Kamu adalah asisten yang membantu dengan penjelasan jelas dan terstruktur."},
                        {"role": "user", "content": user_input}
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )
                answer = response.choices[0].message.content
                st.markdown("### 💬 Jawaban GPT-5:")
                st.write(answer)
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")
