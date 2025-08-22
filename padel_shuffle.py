# Padel Americano Shuffle - Version 1.1
# Fair Shuffle: ensures games played difference is never more than ±1

import streamlit as st
import random
import pandas as pd

# ----------------------------
# Initialize session state
# ----------------------------
if "players" not in st.session_state:
    st.session_state.players = []
if "courts" not in st.session_state:
    st.session_state.courts = 1
if "game_point" not in st.session_state:
    st.session_state.game_point = 21
if "games_played" not in st.session_state:
    st.session_state.games_played = {}
if "scores" not in st.session_state:
    st.session_state.scores = {}
if "leaderboard" not in st.session_state:
    st.session_state.leaderboard = {}
if "active_matches" not in st.session_state:
    st.session_state.active_matches = []

# ----------------------------
# Tournament Setup
# ----------------------------
st.title("🎾 Padel Americano Shuffle - v1.1")

with st.form("setup"):
    players_input = st.text_area("Enter player names (one per line):")
    courts = st.number_input("Number of Courts", min_value=1, max_value=10, value=1)
    game_point = st.number_input("Game Point", min_value=1, value=21)
    submitted = st.form_submit_button("Start Tournament")

if submitted:
    players = [p.strip() for p in players_input.split("\n") if p.strip()]
    st.session_state.players = players
    st.session_state.courts = courts
    st.session_state.game_point = game_point
    st.session_state.games_played = {p: 0 for p in players}
    st.session_state.scores = {p: 0 for p in players}
    st.session_state.leaderboard = {p: {"games": 0, "score": 0} for p in players}
    st.session_state.active_matches = []

# ----------------------------
# Reset Button
# ----------------------------
if st.button("🔄 Reset Tournament"):
    for key in ["players", "courts", "game_point", "games_played", "scores", "leaderboard", "active_matches"]:
        st.session_state[key] = {} if key not in ["players", "active_matches"] else []
    st.experimental_rerun()

# ----------------------------
# Shuffle Function (Fair ±1)
# ----------------------------
def fair_shuffle(players, games_played, courts):
    matches = []
    min_played = min(games_played.values())
    eligible = [p for p in players if games_played[p] <= min_played + 1]

    needed_players = courts * 4
    if len(eligible) < needed_players:
        # If not enough eligible players, include next layer
        next_min = min_played + 2
        eligible = [p for p in players if games_played[p] <= next_min]

    selected = random.sample(eligible, needed_players)
    for c in range(courts):
        p1, p2, p3, p4 = selected[c*4:(c+1)*4]
        matches.append(((p1, p2), (p3, p4)))
    return matches

# ----------------------------
# Active Matches
# ----------------------------
if st.session_state.players:
    if not st.session_state.active_matches:
        st.session_state.active_matches = fair_shuffle(
            st.session_state.players, st.session_state.games_played, st.session_state.courts
        )

    st.header("Current Matches")

    for court_num, match in enumerate(st.session_state.active_matches, 1):
        (p1, p2), (p3, p4) = match
        col1, colvs, col2 = st.columns([3,1,3])

        with col1:
            st.markdown(f"<div style='font-size:24px;font-weight:bold;background:white;padding:10px;border:2px solid black;text-align:center'>{p1} & {p2}</div>", unsafe_allow_html=True)
            if f"score_{court_num}_team1" not in st.session_state:
                st.session_state[f"score_{court_num}_team1"] = 0
            if st.button("⬆️", key=f"up1_{court_num}"):
                if st.session_state[f"score_{court_num}_team1"] < st.session_state.game_point and \
                   st.session_state[f"score_{court_num}_team2"] < st.session_state.game_point - 1:
                    st.session_state[f"score_{court_num}_team1"] += 1
            st.markdown(f"<div style='font-size:28px;font-weight:bold;background:white;padding:10px;border:2px solid black;text-align:center'>{st.session_state[f'score_{court_num}_team1']}</div>", unsafe_allow_html=True)
            if st.button("⬇️", key=f"down1_{court_num}"):
                if st.session_state[f"score_{court_num}_team1"] > 0:
                    st.session_state[f"score_{court_num}_team1"] -= 1

        with colvs:
            st.markdown("<div style='font-size:28px;font-weight:bold;background:white;padding:15px;border:2px solid black;text-align:center'>VS</div>", unsafe_allow_html=True)

        with col2:
            st.markdown(f"<div style='font-size:24px;font-weight:bold;background:white;padding:10px;border:2px solid black;text-align:center'>{p3} & {p4}</div>", unsafe_allow_html=True)
            if f"score_{court_num}_team2" not in st.session_state:
                st.session_state[f"score_{court_num}_team2"] = 0
            if st.button("⬆️", key=f"up2_{court_num}"):
                if st.session_state[f"score_{court_num}_team2"] < st.session_state.game_point and \
                   st.session_state[f"score_{court_num}_team1"] < st.session_state.game_point - 1:
                    st.session_state[f"score_{court_num}_team2"] += 1
            st.markdown(f"<div style='font-size:28px;font-weight:bold;background:white;padding:10px;border:2px solid black;text-align:center'>{st.session_state[f'score_{court_num}_team2']}</div>", unsafe_allow_html=True)
            if st.button("⬇️", key=f"down2_{court_num}"):
                if st.session_state[f"score_{court_num}_team2"] > 0:
                    st.session_state[f"score_{court_num}_team2"] -= 1

    # ----------------------------
    # Complete Round Button
    # ----------------------------
    if st.button("✅ Complete Round"):
        for court_num, match in enumerate(st.session_state.active_matches, 1):
            (p1, p2), (p3, p4) = match
            s1 = st.session_state[f"score_{court_num}_team1"]
            s2 = st.session_state[f"score_{court_num}_team2"]

            st.session_state.leaderboard[p1]["score"] += s1
            st.session_state.leaderboard[p2]["score"] += s1
            st.session_state.leaderboard[p3]["score"] += s2
            st.session_state.leaderboard[p4]["score"] += s2

            st.session_state.leaderboard[p1]["games"] += 1
            st.session_state.leaderboard[p2]["games"] += 1
            st.session_state.leaderboard[p3]["games"] += 1
            st.session_state.leaderboard[p4]["games"] += 1

            st.session_state.games_played[p1] += 1
            st.session_state.games_played[p2] += 1
            st.session_state.games_played[p3] += 1
            st.session_state.games_played[p4] += 1

            st.session_state[f"score_{court_num}_team1"] = 0
            st.session_state[f"score_{court_num}_team2"] = 0

        st.session_state.active_matches = fair_shuffle(
            st.session_state.players, st.session_state.games_played, st.session_state.courts
        )
        st.experimental_rerun()

# ----------------------------
# Leaderboard
# ----------------------------
if st.session_state.players:
    st.header("🏆 Leaderboard")
    df = pd.DataFrame([
        {"Name": name, "Games Played": data["games"], "Total Score": data["score"]}
        for name, data in st.session_state.leaderboard.items()
    ])
    df["Rank"] = df["Total Score"].rank(ascending=False, method="min").astype(int)
    df = df.sort_values(by=["Total Score", "Games Played"], ascending=[False, True])
    st.table(df[["Rank", "Name", "Games Played", "Total Score"]])
