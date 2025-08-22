import streamlit as st
import random

# ============================================================
# 🔹 INITIAL SETUP (Session State)
# ============================================================
if "players" not in st.session_state:
    st.session_state.players = []
if "num_courts" not in st.session_state:
    st.session_state.num_courts = 1
if "round" not in st.session_state:
    st.session_state.round = 0
if "scores" not in st.session_state:
    st.session_state.scores = {}
if "leaderboard" not in st.session_state:
    st.session_state.leaderboard = {}
if "game_point" not in st.session_state:
    st.session_state.game_point = 15
if "matches" not in st.session_state:
    st.session_state.matches = []   # store fixed matches per round

st.title("🎾 Padel Americano Shuffle")

# ============================================================
# 🔹 TOURNAMENT SETUP FORM
# ============================================================
with st.form("setup"):
    names = st.text_area("Enter player names (one per line):")
    num_courts = st.number_input("Number of courts", 1, 10, 1)
    game_point = st.number_input("Game Point", 5, 30, 15)
    start = st.form_submit_button("Start Tournament")

    if start:
        st.session_state.players = [n.strip() for n in names.splitlines() if n.strip()]
        random.shuffle(st.session_state.players)
        st.session_state.num_courts = num_courts
        st.session_state.game_point = game_point
        st.session_state.round = 1
        st.session_state.scores = {}
        st.session_state.leaderboard = {p: 0 for p in st.session_state.players}
        st.session_state.matches = []
        st.rerun()

# ============================================================
# 🔹 RESET BUTTON
# ============================================================
if st.button("🔄 Reset Tournament"):
    st.session_state.players = []
    st.session_state.num_courts = 1
    st.session_state.round = 0
    st.session_state.scores = {}
    st.session_state.leaderboard = {}
    st.session_state.matches = []
    st.rerun()

# ============================================================
# 🔹 ROUND HANDLING
# ============================================================
if st.session_state.round > 0:
    st.subheader(f"Round {st.session_state.round}")

    # --- Generate matches ONCE per round ---
    if not st.session_state.matches:
        players = st.session_state.players.copy()
        random.shuffle(players)
        matches = []
        for c in range(st.session_state.num_courts):
            group = players[c*4:(c+1)*4]
            if len(group) < 4:
                continue
            matches.append(((group[0], group[1]), (group[2], group[3])))
        st.session_state.matches = matches

    # ============================================================
    # 🔹 MATCHES UI (Court Card with Teams & Scores)
    # ============================================================
    for i, ((p1, p2), (p3, p4)) in enumerate(st.session_state.matches):
        key = f"round{st.session_state.round}_court{i}"
        if key not in st.session_state.scores:
            st.session_state.scores[key] = [0, 0]  # [team1, team2]

        s1, s2 = st.session_state.scores[key]
        max_score = st.session_state.game_point

        # --- Court Card Container ---
        st.markdown(
            f"""
            <div style="border:2px solid #444; border-radius:12px; padding:15px; margin:10px 0; background-color:#f9f9f9;">
                <h2 style="text-align:center; margin-top:0;">Court {i+1}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

        col1, col_mid, col2 = st.columns([3, 1, 3])

        # --- Team 1 (Left) ---
        with col1:
            st.markdown(
                f"<div style='border:1px solid #ccc; border-radius:8px; padding:8px; text-align:center; background:#fff;'>"
                f"<b>{p1}</b><br><b>{p2}</b></div>",
                unsafe_allow_html=True
            )
            st.write("")
            if st.button("⬆️", key=f"{key}_t1_up"):
                if s1 + s2 < max_score:
                    s1 += 1
            st.markdown(f"<h2 style='text-align:center;'>{s1}</h2>", unsafe_allow_html=True)
            if st.button("⬇️", key=f"{key}_t1_down"):
                if s1 > 0:
                    s1 -= 1

        # --- Spacer ("VS") ---
        with col_mid:
            st.markdown("<h3 style='text-align:center; margin-top:40px;'>VS</h3>", unsafe_allow_html=True)

        # --- Team 2 (Right) ---
        with col2:
            st.markdown(
                f"<div style='border:1px solid #ccc; border-radius:8px; padding:8px; text-align:center; background:#fff;'>"
                f"<b>{p3}</b><br><b>{p4}</b></div>",
                unsafe_allow_html=True
            )
            st.write("")
            if st.button("⬆️", key=f"{key}_t2_up"):
                if s1 + s2 < max_score:
                    s2 += 1
            st.markdown(f"<h2 style='text-align:center;'>{s2}</h2>", unsafe_allow_html=True)
            if st.button("⬇️", key=f"{key}_t2_down"):
                if s2 > 0:
                    s2 -= 1

        # Save updated scores
        st.session_state.scores[key] = [s1, s2]

    # ============================================================
    # 🔹 COMPLETE ROUND BUTTON
    # ============================================================
    if st.button("✅ Complete Round"):
        for i, ((p1, p2), (p3, p4)) in enumerate(st.session_state.matches):
            key = f"round{st.session_state.round}_court{i}"
            s1, s2 = st.session_state.scores[key]
            st.session_state.leaderboard[p1] += s1
            st.session_state.leaderboard[p2] += s1
            st.session_state.leaderboard[p3] += s2
            st.session_state.leaderboard[p4] += s2

        st.session_state.matches = []  # reset matches for next round
        st.session_state.round += 1
        st.rerun()

    # ============================================================
    # 🔹 LEADERBOARD
    # ============================================================
    st.subheader("🏆 Leaderboard")
    sorted_lb = sorted(st.session_state.leaderboard.items(), key=lambda x: x[1], reverse=True)
    for name, score in sorted_lb:
        st.write(f"{name}: {score}")
