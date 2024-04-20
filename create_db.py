from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.entities import Base, Position, Question, Player
import json

engine = create_engine("sqlite:///rating.db")
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()


with open("data/rating_questions.json", "r") as file:
    data = json.load(file)

# Prepopulate the Position table with known positions
known_positions = ["Forward", "Midfielder", "Defender"]
for pos_name in known_positions:
    if not session.query(Position).filter_by(name=pos_name).first():
        position = Position(name=pos_name)
        session.add(position)
session.commit()

# Print out what is in the database for Positions
print("Positions in Database:")
positions = session.query(Position).all()
for pos in positions:
    print(f"Position: {pos.name} (ID: {pos.id})")

# Populate the database with questions linked to prepopulated positions
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

# Verify and print the inserted data
print("Questions in Database:")
positions = session.query(Position).all()
for pos in positions:
    print(f"Position: {pos.name}")
    for ques in pos.questions:
        print(f"  Question: {ques.content} ({ques.aspect})")

with open("data/players.txt", "r") as file:
    names = file.readlines()

# Clean up names and remove duplicates by using a set
names = set(name.strip() for name in names if name.strip())
print(names)

# Insert each name into the database
for name in names:
    # Check if the player already exists to prevent duplicates
    existing_player = session.query(Player).filter_by(name=name).first()
    if not existing_player:
        player = Player(name=name)
        session.add(player)

session.commit()
session.close()
