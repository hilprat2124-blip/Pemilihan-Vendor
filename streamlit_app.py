import streamlit as st
import random

st.set_page_config(page_title="Batu Gunting Kertas", page_icon="✊", layout="centered")
st.title("✊✋✌️ Batu Gunting Kertas")

# Session state
if "skor_user" not in st.session_state:
    st.session_state.skor_user = 0
    st.session_state.skor_komputer = 0
    st.session_state.hasil = None

pilihan = {"✊ Batu": "batu", "✋ Gunting": "gunting", "✌️ Kertas": "kertas"}

# Skor
col1, col2 = st.columns(2)
col1.metric("👤 Kamu", st.session_state.skor_user)
col2.metric("🤖 Komputer", st.session_state.skor_komputer)

st.divider()

# Tombol pilihan
st.subheader("Pilih senjatamu:")
cols = st.columns(3)
for i, (label, val) in enumerate(pilihan.items()):
    if cols[i].button(label, use_container_width=True):
        komputer = random.choice(list(pilihan.values()))
        user = val

        # Logika menang
        if user == komputer:
            hasil = "🤝 Seri!"
        elif (user == "batu" and komputer == "gunting") or \
             (user == "gunting" and komputer == "kertas") or \
             (user == "kertas" and komputer == "batu"):
            hasil = "🎉 Kamu menang!"
            st.session_state.skor_user += 1
        else:
            hasil = "💀 Kamu kalah!"
            st.session_state.skor_komputer += 1

        st.session_state.hasil = (label, komputer, hasil)
        st.rerun()

# Tampilkan hasil
if st.session_state.hasil:
    user_pick, komp_pick, hasil = st.session_state.hasil
    st.divider()
    c1, c2 = st.columns(2)
    c1.markdown(f"### Kamu: {user_pick}")
    c2.markdown(f"### Komputer: {'✊ Batu' if komp_pick=='batu' else '✋ Gunting' if komp_pick=='gunting' else '✌️ Kertas'}")
    st.markdown(f"## {hasil}")

if st.button("🔄 Reset Skor"):
    st.session_state.skor_user = 0
    st.session_state.skor_komputer = 0
    st.session_state.hasil = None
    st.rerun()
