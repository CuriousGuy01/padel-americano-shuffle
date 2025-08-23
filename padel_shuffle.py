import streamlit as st
import random
import numpy as np

st.set_page_config(page_title="Padel Americano Shuffle", layout="wide")

# ---------------------------
# SESSION STATE INITIALIZATION
# ---------------------------
if "players" not in st.session_state:
    st.session_state["players"] = []
if "scores" not in st.session_state:
    st.session_state["scores"] = {}
if "games_played" not in st.session_state:
    st.session_state["games_played"] = {}
if "results" not in st.session_state:
    st.session_state["results"] = []
if "round" not in st.session_state:
    st.session_state["round"] = 0

# ---------------------------
# FUNCTIONS
# ---------------------------
def exponential_weighting(players, games_played):
    weights = []
    for p in players:
        g = games_played.get(p, 0)
        weights.append(np.exp(-0.5 * g))
    return np.array(weights) / np.sum(weights)

def shuffle_players(players, games_played):
    weights = exponential_weighting(players, games_played)
    return list(np.random.choice(players, size=len(players), replace=False, p=weights))

# ---------------------------
# UI: PLAYER INPUT
# ---------------------------
st.title("🎾 Padel Americano Shuffle 🎾")

with st.sidebar:
    st.header("Setup")
    game_point = st.number_input("Game Point", min_value=1, max_value=50, value=21, step=1)
    num_courts = st.number_input("Number of Courts", min_value=1, value=1, step=1)
    player_name = st.text_input("Add Player Name")
    if st.button("Add Player"):
        if player_name and player_name not in st.session_state["players"]:
            st.session_state["players"].append(player_name)
            st.session_state["scores"][player_name] = 0
            st.session_state["games_played"][player_name] = 0
    if st.button("Reset Tournament"):
        st.session_state["players"] = []
        st.session_state["scores"] = {}
        st.session_state["games_played"] = {}
        st.session_state["results"] = []
        st.session_state["round"] = 0
        st.experimental_rerun()

# ---------------------------
# MAIN TOURNAMENT UI
# ---------------------------
if st.session_state["players"]:
    st.subheader("Players Registered:")
    st.write(", ".join(st.session_state["players"]))

    if st.button("Next Round"):
        st.session_state["round"] += 1
        shuffled = shuffle_players(st.session_state["players"], st.session_state["games_played"])
        st.session_state["active"] = shuffled[: num_courts * 4]
        st.experimental_rerun()

    if "active" in st.session_state:
        active = st.session_state["active"]
        st.markdown(f"## Round {st.session_state['round']}")

        # ---------------------------
        # SCORING UI (Textbox version)
        # ---------------------------
        for c in range(num_courts):
            p1, p2, p3, p4 = active[c*4:(c+1)*4]
            st.markdown(
                f"""
                <div style="border:2px solid black; padding:15px; border-radius:10px; margin-bottom:15px; background-color:white;">
                    <h3 style="text-align:center;">Court {c+1}</h3>
                    <div style="display:flex; justify-content:space-between; align-items:center; font-weight:bold; font-size:20px;">
                        <div style="flex:1; text-align:center;">{p1} & {p2}</div>
                        <div style="flex:1; text-align:center; border:1px solid black; background-color:white; padding:10px; font-weight:bold;">VS</div>
                        <div style="flex:1; text-align:center;">{p3} & {p4}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Input only for Team A
            team_a_score = st.number_input(
                f"Score for {p1} & {p2} (Court {c+1})",
                min_value=0, max_value=game_point, step=1, key=f"scoreA_{c}"
            )
            team_b_score = game_point - team_a_score

            # Save results
            if st.button(f"Complete Match Court {c+1}", key=f"complete_{c}"):
                st.session_state["results"].append(((p1, p2), team_a_score, (p3, p4), team_b_score))
                for p, score in zip([p1, p2], [team_a_score, team_a_score]):
                    st.session_state["scores"][p] += score
                    st.session_state["games_played"][p] += 1
                for p, score in zip([p3, p4], [team_b_score, team_b_score]):
                    st.session_state["scores"][p] += score
                    st.session_state["games_played"][p] += 1
                st.success(f"Result saved for Court {c+1}!")
                st.experimental_rerun()

    # ---------------------------
    # LEADERBOARD
    # ---------------------------
    if st.session_state["scores"]:
        st.subheader("🏆 Leaderboard")
        leaderboard = sorted(
            st.session_state["scores"].items(), key=lambda x: x[1], reverse=True
        )
        st.markdown(
            "<div style='border:2px solid black; padding:10px; background-color:white;'>",
            unsafe_allow_html=True,
        )
        st.write("Rank | Player | Games Played | Total Score")
        st.write("--- | --- | --- | ---")
        for i, (player, score) in enumerate(leaderboard, start=1):
            st.write(f"{i} | {player} | {st.session_state['games_played'][player]} | {score}")
        st.markdown("</div>", unsafe_allow_html=True)
