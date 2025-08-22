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

        # Determine highlight colors
        if s1 > s2:
            color1, color2 = "#d4f7d4", "#f9d6d5"  # green, red
        elif s2 > s1:
            color1, color2 = "#f9d6d5", "#d4f7d4"
        else:
            color1 = color2 = "#f0f0f0"  # neutral gray

        # --- Court Card Container ---
        st.markdown(
            f"""
            <div style="border:2px solid #222; border-radius:12px; padding:15px; margin:10px 0; background-color:#ffffff;">
                <h2 style="text-align:center; margin-top:0; color:#000000;">Court {i+1}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

        col1, col_mid, col2 = st.columns([3, 4, 3])

        # --- Team 1 (Left) ---
        with col1:
            st.markdown(
                f"<div style='border:2px solid #888; border-radius:8px; padding:10px; text-align:center; background:{color1};'>"
                f"<span style='font-size:22px; font-weight:bold; color:#000;'>{p1}</span><br>"
                f"<span style='font-size:22px; font-weight:bold; color:#000;'>{p2}</span></div>",
                unsafe_allow_html=True
            )

        # --- Score & Arrows (Middle) ---
        with col_mid:
            sc1, sc2 = st.columns(2)

            with sc1:
                if st.button("⬆️", key=f"{key}_t1_up"):
                    if s1 + s2 < max_score:
                        s1 += 1
                st.markdown(f"<h1 style='text-align:center; color:#000;'>{s1}</h1>", unsafe_allow_html=True)
                if st.button("⬇️", key=f"{key}_t1_down"):
                    if s1 > 0:
                        s1 -= 1

            with sc2:
                if st.button("⬆️", key=f"{key}_t2_up"):
                    if s1 + s2 < max_score:
                        s2 += 1
                st.markdown(f"<h1 style='text-align:center; color:#000;'>{s2}</h1>", unsafe_allow_html=True)
                if st.button("⬇️", key=f"{key}_t2_down"):
                    if s2 > 0:
                        s2 -= 1

            st.markdown("<h3 style='text-align:center; margin:10px; color:#000;'>VS</h3>", unsafe_allow_html=True)

        # --- Team 2 (Right) ---
        with col2:
            st.markdown(
                f"<div style='border:2px solid #888; border-radius:8px; padding:10px; text-align:center; background:{color2};'>"
                f"<span style='font-size:22px; font-weight:bold; color:#000;'>{p3}</span><br>"
                f"<span style='font-size:22px; font-weight:bold; color:#000;'>{p4}</span></div>",
                unsafe_allow_html=True
            )

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
    # 🔹 LEADERBOARD (Card UI)
    # ============================================================
    st.markdown(
        "<div style='border:2px solid #222; border-radius:12px; padding:15px; margin:20px 0; background-color:#ffffff;'>"
        "<h2 style='text-align:center; color:#000;'>🏆 Leaderboard</h2></div>",
        unsafe_allow_html=True
    )

    sorted_lb = sorted(st.session_state.leaderboard.items(), key=lambda x: x[1], reverse=True)

    for rank, (name, score) in enumerate(sorted_lb, start=1):
        st.markdown(
            f"<div style='border:1px solid #888; border-radius:8px; padding:8px; margin:5px 0; background:#f7f7f7;'>"
            f"<b style='color:#000;'>{rank}. {name}</b> "
            f"<span style='float:right; font-size:18px; font-weight:bold; color:#000;'>{score}</span></div>",
            unsafe_allow_html=True
        )
