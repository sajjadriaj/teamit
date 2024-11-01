import streamlit as st

st.set_page_config(page_title="TeamIt", page_icon="👋", layout="wide")

st.write("# Welcome to TeamIt! 👋")

st.markdown(
    """
    TeamIt is an innovative application designed to help you formulate balanced teams using Machine Learning based on player ratings.
    **👈 Select a feature from the sidebar** to explore what TeamIt can do for you!
    
    ### Features
    - **Manage Players**: Add, update, and manage player information.
    - **Rate Players**: Evaluate and rate players based on various criteria.
    - **Formulate Teams**: Use Machine Learning to create balanced teams.
    - **Log Match Information**: Record and manage match details.
    - **Review Historical Matches**: Analyze past matches and performance.
    
    """
)
