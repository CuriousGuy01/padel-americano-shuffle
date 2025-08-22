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
    st.session_state.game_point = 15   # NEW: Game Point Limit

st.title("🎾 Padel Americano Shuffle")

# ============================================================
# 🔹 TOURNAMENT SETUP FORM
# ============================================================
with st.form("setup"):
    names = st.text_area("Enter player names (one per line):")
    num_courts = st.number_input("Number of courts", 1, 10, 1)

    # NEW: Ask for Game Point
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
        st.rerun()

# ============================================================
# 🔹 ROUND HANDLING
# ============================================================
if st.session_state.round > 0:
    st.subheader(f"Round {st.session_state.round}")

    players = st.session_state.players.copy()
    random.shuffle(players)
    matches = []
    for c in range(st.session_state.num_courts):
        group = players[c*4:(c+1)*4]
        if len(group) < 4:
            continue
        matches.append(((group[0], group[1]), (group[2], group[3])))

    # ============================================================
    # 🔹 MATCHES UI (NEW: Rolling Score Counter)
    # ============================================================
    for i, ((p1, p2), (p3, p4)) in enumerate(matches):
        key = f"round{st.session_state.round}_court{i}"
        if key not in st.session_state.scores:
            st.session_state.scores[key] = [0, 0]  # [score team1, score team2]

        st.write(f"**Court {i+1}: {p1}, {p2} vs {p3}, {p4}**")

        col1, col_mid, col2 = st.columns([1, 0.3, 1])

        # TEAM 1 SCORE COUNTER
        with col1:
            if st.button("⬆️", key=f"{key}_t1_up"):
                if st.session_state.scores[key][0] < st.session_state.game_point:
                    st.session_state.scores[key][0] += 1
            st.markdown(
                f"<h2 style='text-align:center;'>{st.session_state.scores[key][0]}</h2>",
                unsafe_allow_html=True
            )
            if st.button("⬇️", key=f"{key}_t1_down"):
                if st.session_state.scores[key][0] > 0:
                    st.session_state.scores[key][0] -= 1

        # "VS" LABEL
        with col_mid:
            st.markdown("<h3 style='text-align:center;'>vs</h3>", unsafe_allow_html=True)

        # TEAM 2 SCORE COUNTER
        with col2:
            if st.button("⬆️", key=f"{key}_t2_up"):
                if st.session_state.scores[key][1] < st.session_state.game_point:
                    st.session_state.scores[key][1] += 1
            st.markdown(
                f"<h2 style='text-align:center;'>{st.session_state.scores[key][1]}</h2>",
                unsafe_allow_html=True
            )
            if st.button("⬇️", key=f"{key}_t2_down"):
                if st.session_state.scores[key][1] > 0:
                    st.session_state.scores[key][1] -= 1

    # ============================================================
    # 🔹 COMPLETE ROUND BUTTON
    # ============================================================
    if st.button("✅ Complete Round"):
        for i, ((p1, p2), (p3, p4)) in enumerate(matches):
            key = f"round{st.session_state.round}_court{i}"
            s1, s2 = st.session_state.scores[key]
            st.session_state.leaderboard[p1] += s1
            st.session_state.leaderboard[p2] += s1
            st.session_state.leaderboard[p3] += s2
            st.session_state.leaderboard[p4] += s2

        st.session_state.round += 1
        st.rerun()

    # ============================================================
    # 🔹 LEADERBOARD
    # ============================================================
    st.subheader("🏆 Leaderboard")
    sorted_lb = sorted(
        st.session_state.leaderboard.items(), key=lambda x: x[1], reverse=True
    )
    for name, score in sorted_lb:
        st.write(f"{name}: {score}")
