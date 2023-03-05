import os
import sqlalchemy as sq
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    vk_id = sq.Column(sq.Integer, primary_key=True, nullable=False)

    def __str__(self):
        return f'User {self.vk_id})'


class Person(Base):
    __tablename__ = 'person'

    vk_id = sq.Column(sq.Integer, primary_key=True, nullable=False)
    vk_user_id = sq.Column(sq.Integer, sq.ForeignKey('user.vk_id'), primary_key=True, nullable=False)

    user = relationship(User, backref='person')

    def __str__(self):
        return f'Person {self.vk_id}, user {self.vk_user_id})'


load_dotenv()

user_name = os.getenv('NAME')
user_password = os.getenv('PASSWORD')
host = os.getenv('HOST')
port = os.getenv('PORT')
database_name = os.getenv('BASE')

DATABASE_URL = f"postgresql://{user_name}:{user_password}@{host}:{port}/{database_name}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()


def create_tables():
    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def download_user_data(user_id: int):
    if not db.query(User).filter(User.vk_id == user_id).all():
        db.add(User(vk_id=user_id))
        db.commit()
        db.close()


def download_person_data(user_id: int, person_id: int):
    db.add(Person(vk_user_id=user_id, vk_id=person_id))
    db.commit()
    db.close()


def check_person_data(user_id: int, person_id: int):
    if db.query(Person).filter(Person.vk_id == person_id).filter(Person.vk_user_id == user_id).all():
        db.close()
        return True
    db.close()
    return False
