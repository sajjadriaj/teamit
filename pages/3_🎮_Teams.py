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

st.set_page_config(page_title="Teams", page_icon="🎮", layout="wide")


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


def print_teams_as_table(results):
    st.markdown("### Formulated Teams")
    num_teams = len(results)
    headers = [f"Team {i+1}" for i in range(num_teams)]
    
    # Build the Markdown table header
    markdown_table = "| " + " | ".join(headers) + " |\n"
    markdown_table += "| " + " | ".join(["---"] * num_teams) + " |\n"
    
    # Find the maximum team size
    max_team_size = max(len(team_data["team"]) for team_data in results.values())
    
    # Build the table rows
    for i in range(max_team_size):
        row = []
        for team_data in results.values():
            team = list(team_data["team"])
            if i < len(team):
                player = team[i]
                row.append(f"{player} ({team_data['positions'].get(player, 'N/A')})")
            else:
                row.append("")
        markdown_table += "| " + " | ".join(row) + " |\n"
    
    # Remove the separator before the balance scores
    # markdown_table += "| " + " | ".join(["---"] * num_teams) + " |\n"
    
    # Add the balance scores in bold
    balance_scores = []
    for team_data in results.values():
        balance_scores.append(f"**{team_data['balance_score']}**")
    markdown_table += "| " + " | ".join(balance_scores) + " |\n"
    
    st.markdown(markdown_table)


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

    # Input to specify the number of teams to form
    num_teams = st.number_input("Number of teams to form", min_value=2, value=2, step=1)

    # Button to show selected player ratings and generate JSON
    if st.button("Formulate Teams"):
        if selected_players:
            selected_ratings = {player: all_player_ratings[player] for player in selected_players}

            formulator = TeamFormulator(selected_ratings)
            epsilon_greedy = EpsilonGreedy(
                selected_ratings, iterations=1000, epsilon=0.1, num_teams=num_teams
            )

            # Formulate teams using the epsilon-greedy algorithm
            results = formulator.formulate_teams(epsilon_greedy)

            # Print teams as a markdown table
            print_teams_as_table(results)
        else:
            st.write("No players selected.")


app()
