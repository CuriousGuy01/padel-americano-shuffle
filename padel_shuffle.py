import streamlit as st
import random
import numpy as np
import pandas as pd

st.set_page_config(page_title="Padel Americano Shuffle", layout="wide")

# --- Session State Init ---
if "players" not in st.session_state:
    st.session_state.players = []
if "scores" not in st.session_state:
    st.session_state.scores = {}
if "games_played" not in st.session_state:
    st.session_state.games_played = {}
if "round" not in st.session_state:
    st.session_state.round = 1
if "current_matches" not in st.session_state:
    st.session_state.current_matches = []
if "game_point" not in st.session_state:
    st.session_state.game_point = 21

# --- Functions ---
def weighted_shuffle(players, games_played):
    """Exponential weighting: players with fewer games get higher probability."""
    counts = np.array([games_played.get(p, 0) for p in players])
    max_count = counts.max() if len(counts) > 0 else 0
    weights = np.exp(-(counts - max_count))  # exponential bias
    chosen = np.random.choice(players, size=len(players), replace=False, p=weights/weights.sum())
    return list(chosen)

def create_matches(players, num_courts, games_played):
    shuffled = weighted_shuffle(players, games_played)
    matches = []
    for c in range(num_courts):
        if len(shuffled) >= 4:
            p1, p2, p3, p4 = shuffled[:4]
            shuffled = shuffled[4:]
            matches.append(((p1, p2), (p3, p4)))
    return matches

def reset_tournament():
    st.session_state.scores = {}
    st.session_state.games_played = {}
    st.session_state.round = 1
    st.session_state.current_matches = []

# --- Sidebar Input ---
st.sidebar.header("Setup")
players_input = st.sidebar.text_area("Enter player names (one per line):")
num_courts = st.sidebar.number_input("Number of Courts", 1, 10, 1)
game_point = st.sidebar.number_input("Game Point", 1, 50, 21)

if st.sidebar.button("Start Tournament"):
    st.session_state.players = [p.strip() for p in players_input.split("\n") if p.strip()]
    st.session_state.scores = {p: 0 for p in st.session_state.players}
    st.session_state.games_played = {p: 0 for p in st.session_state.players}
    st.session_state.round = 1
    st.session_state.current_matches = create_matches(st.session_state.players, num_courts, st.session_state.games_played)
    st.session_state.game_point = game_point

if st.sidebar.button("Reset Tournament"):
    reset_tournament()

# --- Main UI ---
st.title("🎾 Padel Americano Shuffle")

if st.session_state.players:
    st.subheader(f"Round {st.session_state.round}")

    new_scores = {}

    for court, match in enumerate(st.session_state.current_matches, 1):
        team_a, team_b = match

        with st.container():
            st.markdown(f"### 🟦 Court {court}")
            col1, col2, col3 = st.columns([3, 1, 3])

            with col1:
                st.markdown(
                    f"<div style='border:2px solid black; background:white; padding:10px; font-size:20px; font-weight:bold; text-align:center;'>"
                    f"{team_a[0]} & {team_a[1]}</div>",
                    unsafe_allow_html=True,
                )

            with col2:
                st.markdown(
                    "<div style='border:2px solid black; background:white; padding:10px; font-size:20px; font-weight:bold; text-align:center;'>VS</div>",
                    unsafe_allow_html=True,
                )

            with col3:
                st.markdown(
                    f"<div style='border:2px solid black; background:white; padding:10px; font-size:20px; font-weight:bold; text-align:center;'>"
                    f"{team_b[0]} & {team_b[1]}</div>",
                    unsafe_allow_html=True,
                )

            # Score input
            colA, colB = st.columns(2)
            with colA:
                score_a = st.number_input(
                    f"Score for {team_a[0]} & {team_a[1]}",
                    min_value=0,
                    max_value=st.session_state.game_point,
                    key=f"score_a_{court}_{st.session_state.round}",
                )
                score_b = st.session_state.game_point - score_a
            with colB:
                st.markdown(
                    f"<div style='border:2px solid black; background:white; padding:10px; font-size:18px; font-weight:bold; text-align:center;'>"
                    f"Auto: {score_b}</div>",
                    unsafe_allow_html=True,
                )

            new_scores[(team_a, team_b)] = (score_a, score_b)

    if st.button("✅ Complete Round"):
        for match, (score_a, score_b) in new_scores.items():
            team_a, team_b = match
            for p in team_a:
                st.session_state.scores[p] += score_a
                st.session_state.games_played[p] += 1
            for p in team_b:
                st.session_state.scores[p] += score_b
                st.session_state.games_played[p] += 1

        st.session_state.round += 1
        st.session_state.current_matches = create_matches(
            st.session_state.players, num_courts, st.session_state.games_played
        )
        st.rerun()

    # Leaderboard
    st.subheader("🏆 Leaderboard")
    leaderboard = pd.DataFrame({
        "Player": list(st.session_state.scores.keys()),
        "Games": [st.session_state.games_played[p] for p in st.session_state.scores.keys()],
        "Score": list(st.session_state.scores.values())
    })
    leaderboard = leaderboard.sort_values(by=["Score", "Games"], ascending=[False, True]).reset_index(drop=True)
    leaderboard.index += 1

    # Styled leaderboard table
    st.markdown(
        "<div style='border:3px solid black; background:white; padding:15px; font-size:18px;'>",
        unsafe_allow_html=True,
    )
    st.dataframe(leaderboard, use_container_width=True, height=400)
    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("Enter players in the sidebar and click 'Start Tournament'.")
