import streamlit as st
import random
import pandas as pd

# -------------------- HEADER --------------------
st.title("Padel Americano Tournament")

# -------------------- SESSION STATE --------------------
if "players" not in st.session_state:
    st.session_state.players = []
if "matches" not in st.session_state:
    st.session_state.matches = []
if "scores" not in st.session_state:
    st.session_state.scores = {}
if "games_played" not in st.session_state:
    st.session_state.games_played = {}
if "round" not in st.session_state:
    st.session_state.round = 0

# -------------------- INPUT SECTION --------------------
st.sidebar.header("Setup")
player_input = st.sidebar.text_area("Enter player names (one per line)")
courts = st.sidebar.number_input("Number of Courts", min_value=1, value=1)
game_point = st.sidebar.number_input("Game Point", min_value=1, value=21)

if st.sidebar.button("Start Tournament"):
    st.session_state.players = [p.strip() for p in player_input.split("\n") if p.strip()]
    st.session_state.matches = []
    st.session_state.scores = {}
    st.session_state.games_played = {p: 0 for p in st.session_state.players}
    st.session_state.round = 0
    st.rerun()

# -------------------- SOFT-BIASED SHUFFLE FUNCTION --------------------
def biased_shuffle(players, games_played, courts):
    # Sort players by games played (ascending)
    sorted_players = sorted(players, key=lambda p: (games_played[p], random.random()))
    matches = []
    for c in range(courts):
        if len(sorted_players) >= 4:
            p1, p2, p3, p4 = sorted_players[:4]
            sorted_players = sorted_players[4:]
            matches.append(((p1, p2), (p3, p4)))
    return matches

# -------------------- NEXT ROUND --------------------
if st.button("Next Round"):
    st.session_state.round += 1
    active_matches = biased_shuffle(st.session_state.players, st.session_state.games_played, courts)
    st.session_state.matches = active_matches
    for team1, team2 in active_matches:
        for p in team1 + team2:
            st.session_state.games_played[p] += 1
        st.session_state.scores[(team1, team2)] = [0, 0]
    st.rerun()

# -------------------- MATCH DISPLAY --------------------
if st.session_state.matches:
    st.header(f"Round {st.session_state.round}")

    for i, (team1, team2) in enumerate(st.session_state.matches, 1):
        col1, colvs, col2 = st.columns([4, 1, 4])

        with col1:
            st.markdown(f"<div style='font-size:22px; font-weight:bold; background:white; border:2px solid black; padding:10px; text-align:center'>{team1[0]} & {team1[1]}</div>", unsafe_allow_html=True)
            if st.button("▲", key=f"up1_{i}"):
                if st.session_state.scores[(team1, team2)][0] < game_point and st.session_state.scores[(team1, team2)][0] + st.session_state.scores[(team1, team2)][1] < game_point:
                    st.session_state.scores[(team1, team2)][0] += 1
                    st.rerun()
            st.markdown(f"<div style='font-size:26px; font-weight:bold; background:white; border:2px solid black; padding:10px; text-align:center'>{st.session_state.scores[(team1, team2)][0]}</div>", unsafe_allow_html=True)
            if st.button("▼", key=f"down1_{i}"):
                if st.session_state.scores[(team1, team2)][0] > 0:
                    st.session_state.scores[(team1, team2)][0] -= 1
                    st.rerun()

        with colvs:
            st.markdown(f"<div style='font-size:22px; font-weight:bold; background:white; border:2px solid black; padding:40px 5px; text-align:center'>VS</div>", unsafe_allow_html=True)

        with col2:
            st.markdown(f"<div style='font-size:22px; font-weight:bold; background:white; border:2px solid black; padding:10px; text-align:center'>{team2[0]} & {team2[1]}</div>", unsafe_allow_html=True)
            if st.button("▲", key=f"up2_{i}"):
                if st.session_state.scores[(team1, team2)][1] < game_point and st.session_state.scores[(team1, team2)][0] + st.session_state.scores[(team1, team2)][1] < game_point:
                    st.session_state.scores[(team1, team2)][1] += 1
                    st.rerun()
            st.markdown(f"<div style='font-size:26px; font-weight:bold; background:white; border:2px solid black; padding:10px; text-align:center'>{st.session_state.scores[(team1, team2)][1]}</div>", unsafe_allow_html=True)
            if st.button("▼", key=f"down2_{i}"):
                if st.session_state.scores[(team1, team2)][1] > 0:
                    st.session_state.scores[(team1, team2)][1] -= 1
                    st.rerun()

# -------------------- LEADERBOARD --------------------
st.header("Leaderboard")
leaderboard = pd.DataFrame([
    {"Player": p, "Games Played": st.session_state.games_played[p], "Score": sum(v[i] for (t1, t2), v in st.session_state.scores.items() if p in t1+ t2 and ((i:=0) if p in t1 else (i:=1))==i)}
    for p in st.session_state.players
])
leaderboard = leaderboard.sort_values(by=["Score", "Games Played"], ascending=[False, True]).reset_index(drop=True)
leaderboard.index += 1
leaderboard["Rank"] = leaderboard.index
leaderboard = leaderboard[["Rank", "Player", "Games Played", "Score"]]
st.dataframe(leaderboard, use_container_width=True)
