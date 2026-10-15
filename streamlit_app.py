import streamlit as st
import random

st.set_page_config(page_title="Genetic Breeding", page_icon="🧬", layout="centered")
st.title("🧬 Slime Breeding Lab")
st.caption("Breed 2 slime, lihat gen mana yang turun ke anaknya!")

# Gen: warna (R=merah dominan, r=biru resesif)
COLORS = {"RR": "🔴 Merah", "Rr": "🌸 Pink", "rr": "🔵 Biru"}

if "slimes" not in st.session_state:
    st.session_state.slimes = [
        {"id": 1, "name": "Slime A", "gen": "RR"},
        {"id": 2, "name": "Slime B", "gen": "rr"},
    ]
    st.session_state.babies = []

st.subheader("🧪 Koloni Slime")
cols = st.columns(len(st.session_state.slimes))
for i, s in enumerate(st.session_state.slimes):
    with cols[i]:
        st.markdown(f"### {COLORS[s['gen']]}")
        st.caption(f"{s['name']} — Gen: `{s['gen']}`")

st.divider()
st.subheader("💕 Breeding")

if len(st.session_state.slimes) >= 2:
    names = [s["name"] for s in st.session_state.slimes]
    p1 = st.selectbox("Parent 1", names, key="p1")
    p2 = st.selectbox("Parent 2", names, index=1, key="p2")

    if st.button("🧬 Breed!", use_container_width=True):
        s1 = next(s for s in st.session_state.slimes if s["name"] == p1)
        s2 = next(s for s in st.session_state.slimes if s["name"] == p2)

        # Ambil 1 alel dari masing-masing
        a1 = random.choice(list(s1["gen"]))
        a2 = random.choice(list(s2["gen"]))
        baby_gen = "".join(sorted([a1, a2], key=lambda x: x.lower()))

        baby = {
            "id": len(st.session_state.slimes) + len(st.session_state.babies) + 1,
            "name": f"Baby {len(st.session_state.babies)+1}",
            "gen": baby_gen,
        }
        st.session_state.babies.append(baby)
        st.success(f"🐣 Lahir: {COLORS[baby_gen]} dengan gen `{baby_gen}`!")
        st.balloons()

if st.session_state.babies:
    st.subheader("👶 Anak-anak")
    for b in st.session_state.babies:
        st.write(f"{COLORS[b['gen']]} — `{b['gen']}`")

if st.button("🔄 Reset"):
    st.session_state.clear()
    st.rerun()
