# padel_shuffle.py
# Run locally with: streamlit run padel_shuffle.py

import streamlit as st
import random

st.set_page_config(page_title="Padel Americano Shuffle", page_icon="🎾", layout="centered")

# --- Session state ---
if "players" not in st.session_state:
    st.session_state.players = []
if "games_played" not in st.session_state:
    st.session_state.games_played = {}
if "scores" not in st.session_state:
    st.session_state.scores = {}
if "rest_count" not in st.session_state:
    st.session_state.rest_count = 0
if "round_num" not in st.session_state:
    st.session_state.round_num = 1
if "num_courts" not in st.session_state:
    st.session_state.num_courts = 1
if "current_matches" not in st.session_state:
    st.session_state.current_matches = []

st.title("🎾 Padel Americano Match Generator with Scoring")

# --- Step 1: Setup ---
if not st.session_state.players:
    with st.form("setup_form"):
        num_players = st.number_input("Number of players:", min_value=4, step=1)
        num_courts = st.number_input("Number of courts:", min_value=1, step=1)

        player_names = []
        for i in range(num_players):
            player_names.append(st.text_input(f"Player {i+1} name:"))

        submitted = st.form_submit_button("Start Tournament")
        if submitted:
            st.session_state.players = player_names
            st.session_state.games_played = {p: 0 for p in player_names}
            st.session_state.scores = {p: 0 for p in player_names}
            st.session_state.num_courts = num_courts
            st.session_state.rest_count = max(0, num_players - (num_courts * 4))
            st.rerun()

# --- Step 2: Match display & scoring ---
else:
    st.subheader(f"Round {st.session_state.round_num}")

    # If no current matches saved, generate them
    if not st.session_state.current_matches:
        st.session_state.players.sort(key=lambda x: (st.session_state.games_played[x], random.random()))
        resting = st.session_state.players[-st.session_state.rest_count:] if st.session_state.rest_count > 0 else []
        active = st.session_state.players[:-st.session_state.rest_count] if st.session_state.rest_count > 0 else st.session_state.players[:]
        random.shuffle(active)

        matches = []
        for c in range(st.session_state.num_courts):
            p1, p2, p3, p4 = active[c*4:(c+1)*4]
            matches.append(((p1, p2), (p3, p4)))
            for p in (p1, p2, p3, p4):
                st.session_state.games_played[p] += 1

        matches = []
        for c in range(st.session_state.num_courts):
            group = active[c*4:(c+1)*4]
            if len(group) < 4:  # not enough players for this court
                continue
            p1, p2, p3, p4 = group
            matches.append(((p1, p2), (p3, p4)))
            for p in (p1, p2, p3, p4):
                st.session_state.games_played[p] += 1


        st.session_state.current_matches = matches
        st.session_state.resting_players = resting

    # Score input form
    with st.form("score_form"):
        score_inputs = []
        for court, match in enumerate(st.session_state.current_matches, 1):
            (a, b), (c, d) = match
            col1, col2, col3 = st.columns([3, 1, 3])
            with col1:
                st.markdown(f"**{a} & {b}**")
            with col2:
                score = st.text_input(f"Score Court {court}", key=f"score_{court}", placeholder="e.g. 6-3")
                score_inputs.append((match, score))
            with col3:
                st.markdown(f"**{c} & {d}**")

        if st.session_state.resting_players:
            st.warning(f"Resting: {', '.join(st.session_state.resting_players)}")

        submitted_scores = st.form_submit_button("Submit Scores & Next Round")
        if submitted_scores:
            # Process scores
            for match, score in score_inputs:
                (a, b), (c, d) = match
                try:
                    # Example format: "6-3" or "10-8"
                    s1, s2 = map(int, score.strip().split("-"))
                except:
                    s1, s2 = 0, 0  # Invalid input defaults to 0-0

                st.session_state.scores[a] += s1
                st.session_state.scores[b] += s1
                st.session_state.scores[c] += s2
                st.session_state.scores[d] += s2

            # Prepare for next round
            st.session_state.round_num += 1
            st.session_state.current_matches = []
            st.rerun()

    # Leaderboard display
    st.markdown("---")
    st.subheader("🏆 Leaderboard so far")
    leaderboard = sorted(st.session_state.scores.items(), key=lambda x: x[1], reverse=True)
    for rank, (player, score) in enumerate(leaderboard, 1):
        st.write(f"{rank}. **{player}** — {score} pts")


