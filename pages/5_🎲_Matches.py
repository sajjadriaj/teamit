import streamlit as st
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func  # Add func import
from sqlalchemy.exc import OperationalError
from db.entities import Match, Team, Player, Goal
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Matches", page_icon="🎲", layout="wide")

# Database connection
DATABASE_URL = 'sqlite:///rating.db'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
st.title("Past Matches")

try:
    matches = session.query(Match).all()
except OperationalError as e:
    st.error(f"Database error: {e}")
    st.stop()

# Existing code for displaying past matches
for match in matches:
    with st.expander(f"Match Date: {match.date}"):
        team = session.query(Team).filter(Team.id == match.team_id).first()
        opponent_team = session.query(Team).filter(Team.id == match.opponent_team_id).first()
        
        st.markdown(f"**{team.name}**")
        team_players = session.query(Player).join(Player.player_teams).filter(Player.player_teams.any(team_id=team.id, match_id=match.id)).all()
        team_player_names = ", ".join([player.name for player in team_players])
        st.write(team_player_names)
        
        st.markdown(f"**{opponent_team.name}**")
        opponent_team_players = session.query(Player).join(Player.player_teams).filter(Player.player_teams.any(team_id=opponent_team.id, match_id=match.id)).all()
        opponent_team_player_names = ", ".join([player.name for player in opponent_team_players])
        st.write(opponent_team_player_names)
        
        team_goals = session.query(Goal).filter(Goal.match_id == match.id, Goal.scorer_id.in_([player.id for player in team_players])).count()
        opponent_team_goals = session.query(Goal).filter(Goal.match_id == match.id, Goal.scorer_id.in_([player.id for player in opponent_team_players])).count()
        
        st.write(f"**Score**: {team.name} {team_goals} - {opponent_team.name} {opponent_team_goals}")
        
        if team_goals > opponent_team_goals:
            st.write(f"**Winner**: {team.name}")
        elif team_goals < opponent_team_goals:
            st.write(f"**Winner**: {opponent_team.name}")
        else:
            st.write("**Match Result**: Draw")
        
        team_goal_descriptions = []
        opponent_goal_descriptions = []
        goals = session.query(Goal).filter(Goal.match_id == match.id).all()
        for goal in goals:
            scorer = session.query(Player).filter(Player.id == goal.scorer_id).first()
            assist = session.query(Player).filter(Player.id == goal.assist_id).first() if goal.assist_id else None
            goal_description = f"{scorer.name} (Assist by: {assist.name})" if assist else scorer.name
            if scorer in team_players:
                team_goal_descriptions.append(goal_description)
            else:
                opponent_goal_descriptions.append(goal_description)
        
        st.write(f"**Goals by {team.name}**: " + ", ".join(team_goal_descriptions))
        st.write(f"**Goals by {opponent_team.name}**: " + ", ".join(opponent_goal_descriptions))

# New code for additional statistics and visualizations
st.header("Statistics")

# Top Scorers
st.subheader("Top Scorers")
top_scorers = session.query(Player.name, func.count(Goal.id).label('goals')).join(Goal, Player.id == Goal.scorer_id).group_by(Player.name).order_by(func.count(Goal.id).desc()).limit(10).all()
top_scorers_df = pd.DataFrame(top_scorers, columns=['Player', 'Goals'])
fig_top_scorers = px.bar(top_scorers_df, x='Player', y='Goals', title='Top Scorers')
st.plotly_chart(fig_top_scorers)

# Top Assisters
st.subheader("Top Assisters")
top_assisters = session.query(Player.name, func.count(Goal.id).label('assists')).join(Goal, Player.id == Goal.assist_id).group_by(Player.name).order_by(func.count(Goal.id).desc()).limit(10).all()
top_assisters_df = pd.DataFrame(top_assisters, columns=['Player', 'Assists'])
fig_top_assisters = px.bar(top_assisters_df, x='Player', y='Assists', title='Top Assisters')
st.plotly_chart(fig_top_assisters)

# Most Impactful Players
st.subheader("Most Impactful Players")
impactful_players = session.query(Player.name, func.count(Goal.id).label('impact')).join(Goal, Player.id == Goal.scorer_id).group_by(Player.name).order_by(func.count(Goal.id).desc()).limit(10).all()
impactful_players_df = pd.DataFrame(impactful_players, columns=['Player', 'Impact'])
fig_impactful_players = px.bar(impactful_players_df, x='Player', y='Impact', title='Most Impactful Players')
st.plotly_chart(fig_impactful_players)
