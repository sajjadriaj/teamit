import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.entities import (
    Base,
    Player,
    Position,
    Rating,
)  # Assume these are the same models from previous discussions

st.set_page_config(page_title="Rankings", page_icon="⚽", layout="wide")


# Database connection
engine = create_engine("sqlite:///rating.db")
Session = sessionmaker(bind=engine)
session = Session()


def get_players_with_ratings():
    players = session.query(Player).all()
    positions = session.query(Position).all()
    position_names = [position.name for position in positions]  # Get all position names

    player_data = []
    for player in players:
        ratings_data = {
            pos: [] for pos in position_names
        }  # Initialize all positions with empty list
        for rating in player.ratings:
            position_name = rating.position.name
            ratings_data[position_name].append(rating.score)

        # Compute the average ratings for each position or zero if no ratings
        averaged_ratings = {
            pos: sum(scores) / len(scores) if scores else 0
            for pos, scores in ratings_data.items()
        }
        player_data.append((player, averaged_ratings))
    return player_data


st.title("Player Ratings Overview")

# Fetch player data
player_data = get_players_with_ratings()

# Display player cards in a grid
col_count = 5  # Define the number of columns in the grid
cols = st.columns(col_count)
idx = 0

for player, ratings in player_data:
    with cols[idx % col_count]:
        # Display player name and avatar
        st.image(
            "images/avatar.png", width=150, caption=player.name
        )  # Placeholder avatar image

        # For each position, display the rating and slider aligned tightly
        for position, score in ratings.items():
            st.markdown(f"###### {position}")  # Small header for position name
            st.progress(score / 10)  # Display progress bar as a slider
            st.caption(f"{score:.2f}/10")  # Display numeric score below the slider

    idx += 1
