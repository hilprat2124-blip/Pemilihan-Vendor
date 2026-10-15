import streamlit as st
import random
import time

st.set_page_config(page_title="Pokemon Mini", page_icon="🐾", layout="centered")

# ============ DATA POKEMON ============
POKEDEX = {
    "Charmander": {"emoji": "🔥", "type": "Api",  "hp": 39, "atk": 52, "moves": {"Cakar Api": 15, "Ember": 25, "Gigit": 18}},
    "Squirtle":   {"emoji": "💧", "type": "Air",  "hp": 44, "atk": 48, "moves": {"Water Gun": 22, "Tackle": 15, "Bubble": 18}},
    "Bulbasaur":  {"emoji": "🌿", "type": "Rumput","hp": 45, "atk": 49, "moves": {"Vine Whip": 20, "Tackle": 15, "Razor Leaf": 25}},
    "Pikachu":    {"emoji": "⚡", "type": "Listrik","hp": 35, "atk": 55, "moves": {"Thunder Shock": 25, "Quick Attack": 18, "Tackle": 15}},
    "Rattata":    {"emoji": "🐭", "type": "Normal", "hp": 30, "atk": 56, "moves": {"Tackle": 15, "Bite": 20, "Quick Attack": 18}},
    "Pidgey":     {"emoji": "🐦", "type": "Terbang","hp": 40, "atk": 45, "moves": {"Peck": 18, "Gust": 20, "Tackle": 15}},
    "Caterpie":   {"emoji": "🐛", "type": "Serangga","hp": 45, "atk": 30, "moves": {"Tackle": 15, "Bug Bite": 20}},
    "Zubat":      {"emoji": "🦇", "type": "Terbang","hp": 40, "atk": 45, "moves": {"Leech Life": 20, "Bite": 18, "Gust": 15}},
}

WILD_POOL = ["Rattata", "Pidgey", "Caterpie", "Zubat"]

# ============ STATE INIT ============
def init_game():
    st.session_state.player = None
    st.session_state.team = []
    st.session_state.pokedex_caught = set()
    st.session_state.mode = "starter"  # starter | explore | battle | win | lose
    st.session_state.log = []
    st.session_state.wild = None
    st.session_state.balls = 5
    st.session_state.steps = 0

if "player" not in st.session_state:
    init_game()

def log(msg):
    st.session_state.log.append(msg)
    st.session_state.log = st.session_state.log[-8:]

def spawn_wild():
    name = random.choice(WILD_POOL)
    base = POKEDEX[name]
    level = random.randint(2, 8)
    wild = {
        "name": name, "level": level,
        "hp_max": base["hp"] + level * 3,
        "hp": base["hp"] + level * 3,
        "atk": base["atk"] + level * 2,
        "moves": base["moves"],
        "emoji": base["emoji"],
        "type": base["type"],
    }
    return wild

# ============ HEADER ============
st.title("🐾 Pokemon Mini Adventure")
st.caption("Pilih starter, jelajahi rumput liar, tangkap & lawan Pokemon!")

# ============ SCREEN: PILIH STARTER ============
if st.session_state.mode == "starter":
    st.subheader("🎁 Pilih Pokemon Starter-mu!")

    cols = st.columns(3)
    starters = ["Charmander", "Squirtle", "Bulbasaur"]
    for i, name in enumerate(starters):
        p = POKEDEX[name]
        with cols[i]:
            st.markdown(f"### {p['emoji']} {name}")
            st.write(f"**Tipe:** {p['type']}")
            st.write(f"❤️ HP: {p['hp']}")
            st.write(f"⚔️ ATK: {p['atk']}")
            st.write("**Moves:**")
            for mv, dmg in p["moves"].items():
                st.write(f"- {mv} ({dmg})")
            if st.button(f"Pilih {name}", key=f"pick_{name}", use_container_width=True):
                st.session_state.player = {
                    "name": name, "level": 5,
                    "hp_max": p["hp"] + 15,
                    "hp": p["hp"] + 15,
                    "atk": p["atk"] + 10,
                    "moves": p["moves"],
                    "emoji": p["emoji"], "type": p["type"],
                }
                st.session_state.team = [st.session_state.player]
                st.session_state.pokedex_caught.add(name)
                st.session_state.mode = "explore"
                log(f"✨ Kamu memilih {p['emoji']} {name}!")
                st.rerun()

# ============ SCREEN: EXPLORE ============
elif st.session_state.mode == "explore":
    player = st.session_state.player

    # Kartu status
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader(f"{player['emoji']} {player['name']} Lv.{player['level']}")
        st.progress(player["hp"] / player["hp_max"],
                    text=f"❤️ HP {player['hp']}/{player['hp_max']}")
    with col2:
        st.subheader("🎒 Inventory")
        st.write(f"🔴 Pokeball: **{st.session_state.balls}**")
        st.write(f"👣 Langkah: **{st.session_state.steps}**")
        st.write(f"📖 Pokedex: **{len(st.session_state.pokedex_caught)}/{len(POKEDEX)}**")

    st.divider()

    # Aksi
    c1, c2, c3 = st.columns(3)
    if c1.button("🌿 Jalan di Rumput", use_container_width=True):
        st.session_state.steps += 1
        if random.random() < 0.7:  # 70% ketemu
            st.session_state.wild = spawn_wild()
            st.session_state.mode = "battle"
            log(f"⚠️ Wild {st.session_state.wild['emoji']} {st.session_state.wild['name']} muncul!")
            st.rerun()
        else:
            log("🌾 Nggak ada apa-apa...")
            st.rerun()

    if c2.button("💊 Pakai Potion", use_container_width=True, disabled=player["hp"] >= player["hp_max"]):
        heal = min(20, player["hp_max"] - player["hp"])
        player["hp"] += heal
        log(f"💊 Heal +{heal} HP!")
        st.rerun()

    if c3.button("🔄 Reset Game", use_container_width=True):
        init_game()
        st.rerun()

    # Pokedex mini
    st.divider()
    st.subheader("📖 Pokedex")
    caught = st.session_state.pokedex_caught
    cols = st.columns(len(POKEDEX))
    for i, (name, data) in enumerate(POKEDEX.items()):
        with cols[i]:
            if name in caught:
                st.markdown(f"<div style='text-align:center;font-size:30px'>{data['emoji']}</div>", unsafe_allow_html=True)
                st.caption(f"**{name}**")
            else:
                st.markdown("<div style='text-align:center;font-size:30px;opacity:0.2'>❓</div>", unsafe_allow_html=True)
                st.caption("???")

    # Log
    st.divider()
    st.subheader("📜 Log")
    for l in reversed(st.session_state.log):
        st.write(l)

# ============ SCREEN: BATTLE ============
elif st.session_state.mode == "battle":
    player = st.session_state.player
    wild = st.session_state.wild

    # Tampilan Pokemon
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### 🧑 Kamu")
        st.markdown(f"<div style='font-size:60px'>{player['emoji']}</div>", unsafe_allow_html=True)
        st.write(f"**{player['name']}** Lv.{player['level']}")
        st.progress(player["hp"] / player["hp_max"], text=f"❤️ {player['hp']}/{player['hp_max']}")
    with col2:
        st.markdown("### 👹 Wild")
        st.markdown(f"<div style='font-size:60px'>{wild['emoji']}</div>", unsafe_allow_html=True)
        st.write(f"**{wild['name']}** Lv.{wild['level']}")
        st.progress(wild["hp"] / wild["hp_max"], text=f"❤️ {wild['hp']}/{wild['hp_max']}")

    st.divider()
    st.subheader("⚔️ Pilih Gerakan")

    move_cols = st.columns(len(player["moves"]))
    for i, (mv, dmg) in enumerate(player["moves"].items()):
        if move_cols[i].button(f"{mv}\n({dmg})", use_container_width=True):
            # Player attack
            dmg_dealt = dmg + random.randint(-3, 5)
            wild["hp"] = max(0, wild["hp"] - dmg_dealt)
            log(f"⚔️ {player['name']} pakai {mv}! -{dmg_dealt} HP")

            if wild["hp"] <= 0:
                log(f"🎉 {wild['name']} pingsan! Menang!")
                player["level"] += 1
                player["hp_max"] += 5
                player["atk"] += 2
                player["hp"] = min(player["hp_max"], player["hp"] + 10)
                st.session_state.mode = "explore"
                st.balloons()
                st.rerun()

            # Wild counter attack
            wild_move = random.choice(list(wild["moves"].items()))
            wild_dmg = wild_move[1] + random.randint(-2, 3)
            player["hp"] = max(0, player["hp"] - wild_dmg)
            log(f"👹 {wild['name']} pakai {wild_move[0]}! -{wild_dmg} HP")

            if player["hp"] <= 0:
                log("💀 Pokemon-mu pingsan...")
                st.session_state.mode = "lose"
                st.rerun()
            st.rerun()

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button(f"🔴 Lempar Pokeball ({st.session_state.balls})",
                     use_container_width=True,
                     disabled=st.session_state.balls <= 0):
            st.session_state.balls -= 1
            # Chance tangkap = lebih tinggi kalau HP wild rendah
            hp_ratio = wild["hp"] / wild["hp_max"]
            catch_chance = 0.9 - hp_ratio * 0.6  # 30% - 90%
            st.write(f"🎯 Chance: {catch_chance*100:.0f}%")
            if random.random() < catch_chance:
                log(f"✨ Berhasil menangkap {wild['name']}!")
                st.session_state.pokedex_caught.add(wild["name"])
                st.session_state.mode = "explore"
                st.balloons()
                time.sleep(0.5)
                st.rerun()
            else:
                log(f"💨 {wild['name']} kabur dari Pokeball!")
                # Wild counter
                wild_move = random.choice(list(wild["moves"].items()))
                wild_dmg = wild_move[1]
                player["hp"] = max(0, player["hp"] - wild_dmg)
                log(f"👹 {wild['name']} pakai {wild_move[0]}! -{wild_dmg} HP")
                if player["hp"] <= 0:
                    st.session_state.mode = "lose"
                st.rerun()
    with c2:
        if st.button("🏃 Kabur", use_container_width=True):
            if random.random() < 0.7:
                log("🏃 Berhasil kabur!")
                st.session_state.mode = "explore"
            else:
                log("❌ Gagal kabur!")
                wild_move = random.choice(list(wild["moves"].items()))
                wild_dmg = wild_move[1]
                player["hp"] = max(0, player["hp"] - wild_dmg)
                log(f"👹 {wild['name']} pakai {wild_move[0]}! -{wild_dmg} HP")
                if player["hp"] <= 0:
                    st.session_state.mode = "lose"
            st.rerun()

    # Log
    st.divider()
    st.subheader("📜 Log Pertarungan")
    for l in reversed(st.session_state.log):
        st.write(l)

# ============ SCREEN: LOSE ============
elif st.session_state.mode == "lose":
    st.error("💀 Kamu kalah! Pokemon-mu pingsan...")
    st.markdown("<div style='text-align:center;font-size:80px'>😵</div>", unsafe_allow_html=True)
    st.write(f"📊 Total langkah: **{st.session_state.steps}**")
    st.write(f"📖 Pokemon tertangkap: **{len(st.session_state.pokedex_caught)}**")
    if st.button("🔄 Main Lagi", use_container_width=True):
        init_game()
        st.rerun()
