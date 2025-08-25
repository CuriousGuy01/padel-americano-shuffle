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

    def score_callback(score_key, other_score_key, last_edited_key):
        # Only update inside callback!
        st.session_state[last_edited_key] = score_key
        value = st.session_state[score_key]
        value = max(0, min(value, st.session_state.game_point))  # clamp
        st.session_state[score_key] = value
        st.session_state[other_score_key] = st.session_state.game_point - value

    for court, match in enumerate(st.session_state.current_matches, 1):
        team_a, team_b = match

        with st.container():
            st.markdown(f"### 🟦 Court {court}")
            col1, col2, col3 = st.columns([3, 1, 3])

            with col1:
                st.markdown(
                    f"<div style='border:2px solid black; background:white; padding:10px; font-size:22px; font-weight:bold; text-align:center; color:black;'>"
                    f"{team_a[0]} & {team_a[1]}</div>",
                    unsafe_allow_html=True,
                )

            with col2:
                st.markdown(
                    "<div style='border:2px solid black; background:white; padding:10px; font-size:22px; font-weight:bold; text-align:center; color:black;'>VS</div>",
                    unsafe_allow_html=True,
                )

            with col3:
                st.markdown(
                    f"<div style='border:2px solid black; background:white; padding:10px; font-size:22px; font-weight:bold; text-align:center; color:black;'>"
                    f"{team_b[0]} & {team_b[1]}</div>",
                    unsafe_allow_html=True,
                )

            score_a_key = f"score_a_{court}_{st.session_state.round}"
            score_b_key = f"score_b_{court}_{st.session_state.round}"
            last_edited_key = f"last_edited_{court}_{st.session_state.round}"

            # Only initialize if not present!
            if score_a_key not in st.session_state:
                st.session_state[score_a_key] = 0
            if score_b_key not in st.session_state:
                st.session_state[score_b_key] = st.session_state.game_point
            if last_edited_key not in st.session_state:
                st.session_state[last_edited_key] = score_a_key

            colA, colB = st.columns(2)
            with colA:
                st.number_input(
                    f"Score for {team_a[0]} & {team_a[1]} (0-{st.session_state.game_point})",
                    min_value=0,
                    max_value=st.session_state.game_point,
                    value=st.session_state[score_a_key],
                    key=score_a_key,
                    on_change=score_callback,
                    args=(score_a_key, score_b_key, last_edited_key),
                )
            with colB:
                st.number_input(
                    f"Score for {team_b[0]} & {team_b[1]} (0-{st.session_state.game_point})",
                    min_value=0,
                    max_value=st.session_state.game_point,
                    value=st.session_state[score_b_key],
                    key=score_b_key,
                    on_change=score_callback,
                    args=(score_b_key, score_a_key, last_edited_key),
                )

            score_a_val = st.session_state[score_a_key]
            score_b_val = st.session_state[score_b_key]

            new_scores[(team_a, team_b)] = (score_a_val, score_b_val)

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
        "<div style='border:3px solid black; background:white; padding:15px; font-size:20px; color:black;'>",
        unsafe_allow_html=True,
    )
    st.dataframe(leaderboard, use_container_width=True, height=400)
    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("Enter players in the sidebar and click 'Start Tournament'.")
