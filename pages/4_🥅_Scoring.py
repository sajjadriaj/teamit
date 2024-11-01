import streamlit as st
try:
    from streamlit_sortables import sort_items
except ImportError:
    st.error("The 'streamlit-sortables' module is not installed. Please install it using 'pip install streamlit-sortables'.")
    st.stop()

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from db.entities import Player, Team, Match, Goal, PlayerTeam
from datetime import datetime

st.set_page_config(page_title="Score", page_icon="🥅", layout="wide")

# ...existing code...

# Database connection
engine = create_engine('sqlite:///rating.db')
Session = sessionmaker(bind=engine)
session = Session()

try:
    # Fetch existing players
    players = session.query(Player).all()
    player_options = [player.name for player in players]

    # Initialize session state variables for player assignments
    if 'available_players' not in st.session_state:
        st.session_state['available_players'] = player_options
    if 'team1_players' not in st.session_state:
        st.session_state['team1_players'] = []
    if 'team2_players' not in st.session_state:
        st.session_state['team2_players'] = []
    if 'team1_goals' not in st.session_state:
        st.session_state['team1_goals'] = []
    if 'team2_goals' not in st.session_state:
        st.session_state['team2_goals'] = []

    # Streamlit page
    st.title("Match Scoring")

    st.subheader("Match Information")
    team1_name = st.text_input("Enter Team 1 Name", key='team1')
    team2_name = st.text_input("Enter Team 2 Name", key='team2')
    match_date = st.date_input("Match Date", datetime.now())

    st.subheader("Assign Players to Teams")

    # Prepare the data for sort_items
    original_items = [
        {'header': 'Available Players', 'items': st.session_state['available_players']},
        {'header': team1_name or 'Team 1', 'items': st.session_state['team1_players']},
        {'header': team2_name or 'Team 2', 'items': st.session_state['team2_players']}
    ]

    # Use sort_items to create sortable lists
    sorted_items = sort_items(original_items, multi_containers=True, key='player_sort')

    # Update session state with the sorted items
    st.session_state['available_players'] = sorted_items[0]['items']
    st.session_state['team1_players'] = sorted_items[1]['items']
    st.session_state['team2_players'] = sorted_items[2]['items']

    st.subheader("Goals")

    # Add goals for Team 1
    st.markdown(f"### {team1_name or 'Team 1'} Goals")
    if st.button("Add Goal for Team 1", key='add_goal_team1'):
        st.session_state['team1_goals'].append({'scorer': None, 'assist': None})

    for i, goal in enumerate(st.session_state['team1_goals']):
        st.markdown(f"**Goal {i+1}**")
        scorer_name = st.selectbox(f"Scorer for Goal {i+1}", st.session_state['team1_players'], key=f"team1_scorer_{i}")
        assist_name = st.selectbox(f"Assist for Goal {i+1} (Optional)", ["None"] + st.session_state['team1_players'], key=f"team1_assist_{i}")
        st.session_state['team1_goals'][i] = {'scorer': scorer_name, 'assist': assist_name if assist_name != "None" else None}

    # Add goals for Team 2
    st.markdown(f"### {team2_name or 'Team 2'} Goals")
    if st.button("Add Goal for Team 2", key='add_goal_team2'):
        st.session_state['team2_goals'].append({'scorer': None, 'assist': None})

    for i, goal in enumerate(st.session_state['team2_goals']):
        st.markdown(f"**Goal {i+1}**")
        scorer_name = st.selectbox(f"Scorer for Goal {i+1}", st.session_state['team2_players'], key=f"team2_scorer_{i}")
        assist_name = st.selectbox(f"Assist for Goal {i+1} (Optional)", ["None"] + st.session_state['team2_players'], key=f"team2_assist_{i}")
        st.session_state['team2_goals'][i] = {'scorer': scorer_name, 'assist': assist_name if assist_name != "None" else None}

    if st.button("Submit"):
        # Create Team 1
        team1 = Team(name=team1_name)
        session.add(team1)
        session.commit()

        # Create Team 2
        team2 = Team(name=team2_name)
        session.add(team2)
        session.commit()

        # Create a new match
        match = Match(date=match_date, team=team1, opponent_team=team2)
        session.add(match)
        session.commit()

        # Add goals to the match
        for goal_info in st.session_state['team1_goals'] + st.session_state['team2_goals']:
            scorer = session.query(Player).filter_by(name=goal_info['scorer']).first()
            assist = session.query(Player).filter_by(name=goal_info['assist']).first() if goal_info['assist'] else None
            goal = Goal(match_id=match.id, scorer_id=scorer.id, assist_id=assist.id if assist else None)
            session.add(goal)

        # Assign players to Team 1
        for player_name in st.session_state['team1_players']:
            player = session.query(Player).filter_by(name=player_name).first()
            player_team = PlayerTeam(player_id=player.id, team_id=team1.id, match_id=match.id)
            session.add(player_team)

        # Assign players to Team 2
        for player_name in st.session_state['team2_players']:
            player = session.query(Player).filter_by(name=player_name).first()
            player_team = PlayerTeam(player_id=player.id, team_id=team2.id, match_id=match.id)
            session.add(player_team)

        session.commit()
        st.success("Match, goals, and player assignments have been saved successfully.")
except Exception as e:
    st.error(f"An error occurred: {e}")

# ...existing code...
