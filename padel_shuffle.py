# Save this file as padel_shuffle.py
# Run with: streamlit run padel_shuffle.py

import streamlit as st
import random

st.set_page_config(page_title="Padel Americano Shuffle", page_icon="🎾", layout="centered")

# Session state to store data between rounds
if "players" not in st.session_state:
    st.session_state.players = []
if "games_played" not in st.session_state:
    st.session_state.games_played = {}
if "rest_count" not in st.session_state:
    st.session_state.rest_count = 0
if "round_num" not in st.session_state:
    st.session_state.round_num = 1
if "num_courts" not in st.session_state:
    st.session_state.num_courts = 1

st.title("🎾 Padel Americano Match Generator")

# Step 1: Setup (only runs once)
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
            st.session_state.num_courts = num_courts
            st.session_state.rest_count = max(0, num_players - (num_courts * 4))
            st.experimental_rerun()

# Step 2: Show current round
else:
    st.subheader(f"Round {st.session_state.round_num}")

    # Sort by fewest games played to balance
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

    for court, match in enumerate(matches, 1):
        (a, b), (c, d) = match
        st.write(f"**Court {court}:** {a} & {b} vs {c} & {d}")
    if resting:
        st.warning(f"Resting: {', '.join(resting)}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Next Round"):
            st.session_state.round_num += 1
            st.experimental_rerun()
    with col2:
        if st.button("Show Summary"):
            summary = "\n".join([f"{p}: {st.session_state.games_played[p]} games" for p in st.session_state.players])
            st.info(summary)
