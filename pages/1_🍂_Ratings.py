import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.entities import Base, Position, Player, Question, Rating


st.set_page_config(page_title="Ratings", page_icon="🍂", layout="wide")

engine = create_engine("sqlite:///rating.db")
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()


def get_players():
    """Fetch all players from the database."""
    return session.query(Player).all()


def get_positions():
    """Fetch all positions from the database."""
    return session.query(Position).all()


def load_questions():
    """Load questions for each position from the database"""
    positions = session.query(Position).all()
    pos_questions = {}
    for pos in positions:
        pos_questions[pos.name] = [(q.content, q.aspect) for q in pos.questions]
    return pos_questions


def submit_ratings(player_id, position_id, responses):
    """Submit ratings to the database."""
    for question_id, score in responses.items():
        rating = Rating(
            player_id=player_id,
            position_id=position_id,
            question_id=question_id,
            score=score,
        )
        session.add(rating)
    session.commit()
    st.success("Ratings submitted successfully!")


st.title("Soccer Player Rating System")

# Load data from the database
players = get_players()
positions = get_positions()
pos_questions = load_questions()

# Dropdown for player selection
player_options = {player.name: player.id for player in players}
player_name = st.selectbox("Select Player:", list(player_options.keys()))
player_id = player_options[player_name] if player_name else None

# Radio buttons for position selection
position_options = {pos.name: pos.id for pos in positions}
position_name = st.radio("Select Player Position:", list(position_options.keys()))
position_id = position_options[position_name] if position_name else None

# Display questions and collect ratings if both player and position are selected
if player_name and position_name:
    questions = session.query(Question).filter_by(position_id=position_id).all()
    responses = {}
    st.subheader(f"Rating Questions for {position_name}:")
    for question in questions:
        score = st.slider(
            question.content, 0, 10, 5, help=f"Evaluating {question.aspect}"
        )
        responses[question.id] = score

    # Submit button
    if st.button("Submit Ratings"):
        submit_ratings(player_id, position_id, responses)
