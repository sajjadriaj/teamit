from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.entities import Base, Player

engine = create_engine("sqlite:///../rating.db")
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()


def insert_user(email, username, password):
    """
    Inserts a user into the database.
    """
    new_user = Player(email=email, username=username, password=password)
    session.add(new_user)
    session.commit()
    return new_user


def fetch_users():
    """
    Fetches all users from the database.
    """
    users = session.query(Player).all()
    return {user.email: user for user in users}


def get_user_emails():
    """
    Fetches all user emails from the database.
    """
    users = session.query(Player).all()
    return [user.email for user in users]


def get_usernames():
    """
    Fetches all usernames from the database.
    """
    users = session.query(Player).all()
    return [user.username for user in users]
