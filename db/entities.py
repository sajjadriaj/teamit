from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    ratings = relationship("Rating", back_populates="player")  # Link ratings to players


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
