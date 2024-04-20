import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.entities import (
    Base,
    Player,
    Position,
    Rating,
)  # Assume these are the same models from previous discussions
import json
from models.bandits import EpsilonGreedy, UCB, ThompsonSampling
from models.base import TeamFormulator

st.set_page_config(page_title="Teams", page_icon="👋", layout="wide")


# Database connection
engine = create_engine("sqlite:///rating.db")
Session = sessionmaker(bind=engine)
session = Session()


def get_all_players_ratings():
    # Query all players
    players = session.query(Player).all()
    # Query all positions once to optimize
    positions = session.query(Position).all()
    position_names = [
        pos.name.lower() for pos in positions
    ]  # Convert position names to lowercase

    player_ratings = {}
    for player in players:
        ratings = {
            pos: [] for pos in position_names
        }  # Initialize ratings for each position in lowercase
        for rating in player.ratings:
            position_name = (
                rating.position.name.lower()
            )  # Ensure position name is in lowercase
            ratings[position_name].append(rating.score)

        # Compute average or zero if no ratings
        averaged_ratings = {
            pos: sum(scores) / len(scores) if scores else 0
            for pos, scores in ratings.items()
        }
        player_ratings[player.name] = averaged_ratings

    return player_ratings


def print_teams(team_name, team_data):
    st.subheader(f"{team_name} (Balance Score: {team_data['balance_score']})")
    position_players = {"forward": [], "midfielder": [], "defender": []}
    position_scores = {"forward": 0, "midfielder": 0, "defender": 0}

    # Extract player positions and their scores
    for player, position in team_data["positions"].items():
        position_players[position].append(player)
        position_scores[position] += team_data["team"][player][position]

    # Display players grouped by positions and their scores
    for position in ["forward", "midfielder", "defender"]:
        pos_total = position_scores[position]
        num_players = len(position_players[position])
        pos_avg_score = pos_total / num_players if num_players > 0 else 0
        st.markdown(f"**{position.capitalize()} (Score: {pos_avg_score:.2f}):**")
        for player in position_players[position]:
            st.text(f"    - {player}")
        st.text(f"    Overall {position.capitalize()} Score: {pos_total}")
        st.write("")  # Add some spacing


def app():
    st.title("Player Ratings Overview")

    # Fetch all player ratings
    all_player_ratings = get_all_players_ratings()

    # Grid selection for players
    player_names = list(all_player_ratings.keys())
    num_cols = 3  # Number of columns in the grid
    cols = st.columns(num_cols)
    selected_players = []

    # Iterate over player names and create a checkbox in the grid for each player
    for idx, player_name in enumerate(player_names):
        with cols[idx % num_cols]:
            if st.checkbox(player_name, key=player_name):
                selected_players.append(player_name)

    # Button to show selected player ratings and generate JSON
    if st.button("Show Selected Player Ratings"):
        if selected_players:
            st.subheader("Selected Players and Their Ratings:")
            selected_ratings = {}
            for player in selected_players:
                ratings = all_player_ratings.get(player, {})
                selected_ratings[player] = ratings
                # st.markdown(f"**{player}**")
                # for position, score in ratings.items():
                #     st.write(f"{position}: {score:.2f}/10")

            formulator = TeamFormulator(selected_ratings)
            epsilon_greedy = EpsilonGreedy(
                selected_ratings, iterations=1000, epsilon=0.1
            )

            # Formulate teams using the epsilon-greedy algorithm
            results = formulator.formulate_teams(epsilon_greedy)
            col1, col2 = st.columns(2)
            with col1:
                print_teams("Team 1", results["Team 1"])
            with col2:
                print_teams("Team 2", results["Team 2"])

            # Display the JSON for the selected players
            # selected_json = json.dumps(selected_ratings, indent=4)
            # st.text_area("JSON Output for Selected Players:", selected_json, height=200)
        else:
            st.write("No players selected.")


app()
