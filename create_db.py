from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.entities import Base, Position, Question, Player, Rating, Team, Match, PlayerTeam, Goal
import json

engine = create_engine("sqlite:///rating.db")

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

def drop_all_tables(engine):
    Base.metadata.drop_all(engine)

def prepopulate_positions(session):
    known_positions = ["Forward", "Midfielder", "Defender"]
    for pos_name in known_positions:
        if not session.query(Position).filter_by(name=pos_name).first():
            position = Position(name=pos_name)
            session.add(position)
    session.commit()

def populate_questions(session):
    with open("data/rating_questions.json", "r") as file:
        data = json.load(file)
    
    for position_name, questions in data.items():
        position = session.query(Position).filter_by(name=position_name).first()
        if position:
            for question_info in questions:
                question = Question(
                    content=question_info["question"],
                    aspect=question_info["aspect"],
                    position=position,
                )
                session.add(question)
        else:
            print(f"Position not found in the database: {position_name}")
    session.commit()

def insert_players(session, drop_existing=False):
    if drop_existing:
        session.query(Player).delete()
        session.commit()
    
    with open("data/players.txt", "r") as file:
        names = file.readlines()
    
    names = set(name.strip() for name in names if name.strip())
    print(names)
    
    for name in names:
        existing_player = session.query(Player).filter_by(name=name).first()
        if not existing_player:
            player = Player(name=name)
            session.add(player)
    
    session.commit()

def populate_ratings(session, clear_existing=False):
    if clear_existing:
        session.query(Rating).delete()
        session.commit()
    
    with open("data/initial_rating.json", "r") as file:
        data = json.load(file)
    
    for player_name, ratings in data.items():
        player = session.query(Player).filter_by(name=player_name).first()
        if player:
            for question_content, score in ratings.items():
                question = session.query(Question).filter_by(content=question_content).first()
                if question:
                    rating = Rating(
                        player_id=player.id,
                        position_id=question.position_id,
                        question_id=question.id,
                        score=score
                    )
                    session.add(rating)
                else:
                    print(f"Question not found in the database: {question_content}")
        else:
            print(f"Player not found in the database: {player_name}")
    session.commit()

def main():
    # drop_all_tables(engine)
    # Base.metadata.create_all(engine)
    # prepopulate_positions(session)
    # populate_questions(session)
    insert_players(session, drop_existing=True)
    populate_ratings(session, clear_existing=True)
    session.close()

if __name__ == "__main__":
    main()
