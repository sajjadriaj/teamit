from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    ratings = relationship("Rating", back_populates="player")  # Link ratings to players
    player_teams = relationship("PlayerTeam", back_populates="player")  # Link players to player_teams
    goals = relationship("Goal", foreign_keys="[Goal.scorer_id]", back_populates="scorer")  # Link players to goals as scorers
    assists = relationship("Goal", foreign_keys="[Goal.assist_id]", back_populates="assist")  # Link players to goals as assisters


class Position(Base):
    __tablename__ = "positions"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    questions = relationship(
        "Question", back_populates="position"
    )  # Link questions to positions
    ratings = relationship(
        "Rating", back_populates="position"
    )  # Link ratings to positions


class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True)
    content = Column(String, nullable=False)
    aspect = Column(String)
    position_id = Column(
        Integer, ForeignKey("positions.id")
    )  # Ensure ForeignKey is defined
    position = relationship("Position", back_populates="questions")


class Rating(Base):
    __tablename__ = "ratings"
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"))  # ForeignKey to players
    position_id = Column(Integer, ForeignKey("positions.id"))  # ForeignKey to positions
    score = Column(Float)
    player = relationship("Player", back_populates="ratings")
    position = relationship(
        "Position", back_populates="ratings"
    )  # Link back to position
    question_id = Column(Integer, ForeignKey("questions.id"))  # ForeignKey to questions
    question = relationship("Question")  # Link ratings to specific questions


class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)  # Removed unique constraint
    matches = relationship("Match", back_populates="team", foreign_keys="[Match.team_id]")
    player_teams = relationship("PlayerTeam", back_populates="team")  # Link teams to player_teams


class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"))
    team = relationship("Team", back_populates="matches", foreign_keys=[team_id])
    opponent_team_id = Column(Integer, ForeignKey("teams.id"))
    opponent_team = relationship("Team", foreign_keys=[opponent_team_id])
    goals = relationship("Goal", back_populates="match")  # Link matches to goals


class PlayerTeam(Base):
    __tablename__ = "player_teams"
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))
    match_id = Column(Integer, ForeignKey("matches.id"))
    player = relationship("Player", back_populates="player_teams")
    team = relationship("Team", back_populates="player_teams")
    match = relationship("Match")


class Goal(Base):
    __tablename__ = "goals"
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    match = relationship("Match", back_populates="goals")
    scorer_id = Column(Integer, ForeignKey("players.id"))
    scorer = relationship("Player", foreign_keys=[scorer_id], back_populates="goals")
    assist_id = Column(Integer, ForeignKey("players.id"), nullable=True)
    assist = relationship("Player", foreign_keys=[assist_id], back_populates="assists")