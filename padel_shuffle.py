import streamlit as st
import random
import math
import pandas as pd

st.set_page_config(page_title="Padel Americano Shuffle", layout="wide")

# --- Session State Initialization ---
if "players" not in st.session_state:
    st.session_state.players = []
if "scores" not in st.session_state:
    st.session_state.scores = {}
if "games_played" not in st.session_state:
    st.session_state.games_played = {}
if "round" not in st.session_state:
    st.session_state.round = 0
if "active_matches" not in st.session_state:
    st.session_state.active_matches = []

# --- Inputs ---
st.title("🎾 Padel Americano Shuffle")

num_courts = st.number_input("Number of Courts", min_value=1, value=1)
game_point = st.number_input("Game Point", min_value=1, value=21)

player_input = st.text_area("Enter player names (one per line)")
if st.button("Set Players"):
    st.session_state.players = [p.strip() for p in player_input.split("\n") if p.strip()]
    st.session_state.scores = {p: 0 for p in st.session_state.players}
    st.session_state.games_played = {p: 0 for p in st.session_state.players}
    st.session_state.round = 0
    st.session_state.active_matches = []
    st.rerun()

# --- Weighted Shuffle ---
def weighted_shuffle(players, games_played):
    weights = [math.exp(-games_played[p]) for p in players]
    chosen = random.choices(players, weights=weights, k=len(players))
    seen = set()
    unique = []
    for c in chosen:
        if c not in seen:
            unique.append(c)
            seen.add(c)
    return unique

# --- Start Next Round ---
if st.button("Next Round"):
    if len(st.session_state.players) >= 4:
        st.session_state.round += 1
        shuffled = weighted_shuffle(st.session_state.players, st.session_state.games_played)
        matches = []
        for c in range(num_courts):
            if len(shuffled) >= 4:
                p1, p2, p3, p4 = shuffled[:4]
                shuffled = shuffled[4:]
                matches.append(((p1, p2), (p3, p4)))
                for p in [p1, p2, p3, p4]:
                    st.session_state.games_played[p] += 1
        st.session_state.active_matches = matches
        st.rerun()

# --- Display Matches with Score Entry ---
if st.session_state.active_matches:
    st.subheader(f"Round {st.session_state.round}")

    for i, match in enumerate(st.session_state.active_matches):
        team_a, team_b = match
        st.markdown(f"""
        <div style='border:2px solid black; padding:15px; margin:10px; background:white; text-align:center;'>
            <span style='font-size:20px; font-weight:bold;'>{team_a[0]} & {team_a[1]}</span>
            <span style='margin:0 20px; font-size:22px; font-weight:bold; border:1px solid black; padding:5px; background:white;'>VS</span>
            <span style='font-size:20px; font-weight:bold;'>{team_b[0]} & {team_b[1]}</span>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            score_a = st.number_input(f"Score for {team_a[0]} & {team_a[1]}", min_value=0, max_value=game_point, key=f"score_a_{i}")
        with col2:
            score_b = game_point - score_a
            st.markdown(f"<div style='border:2px solid black; background:white; padding:10px; text-align:center; font-size:18px; font-weight:bold;'>{score_b}</div>", unsafe_allow_html=True)

        if st.button(f"Complete Match {i+1}"):
            st.session_state.scores[team_a[0]] += score_a
            st.session_state.scores[team_a[1]] += score_a
            st.session_state.scores[team_b[0]] += score_b
            st.session_state.scores[team_b[1]] += score_b
            st.session_state.active_matches[i] = None
            st.rerun()

    st.session_state.active_matches = [m for m in st.session_state.active_matches if m]

# --- Leaderboard ---
if st.session_state.players:
    st.subheader("🏆 Leaderboard")
    df = pd.DataFrame({
        "Player": list(st.session_state.scores.keys()),
        "Games Played": [st.session_state.games_played[p] for p in st.session_state.players],
        "Total Score": [st.session_state.scores[p] for p in st.session_state.players]
    })
    df = df.sort_values(by=["Total Score", "Games Played"], ascending=[False, True]).reset_index(drop=True)
    df.index = df.index + 1
    st.markdown("<div style='border:2px solid black; background:white; padding:10px;'>", unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- Reset Tournament ---
if st.button("Reset Tournament"):
    st.session_state.players = []
    st.session_state.scores = {}
    st.session_state.games_played = {}
    st.session_state.round = 0
    st.session_state.active_matches = []
    st.rerun()
