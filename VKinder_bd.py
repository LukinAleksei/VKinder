import os
import sqlalchemy as sq
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = sq.Column(sq.Integer, primary_key=True, nullable=False)
    name = sq.Column(sq.String(length=60), nullable=False)
    surname = sq.Column(sq.String(length=60), nullable=False)
    age = sq.Column(sq.Integer, nullable=False)
    city = sq.Column(sq.String(length=60), nullable=False)

    def __str__(self):
        return f'User {self.id})'


class Person(Base):
    __tablename__ = 'person'

    id = sq.Column(sq.Integer, primary_key=True, nullable=False)
    name = sq.Column(sq.String(length=60), nullable=False)
    surname = sq.Column(sq.String(length=60), nullable=False)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('user.id'), primary_key=True, nullable=False)

    user = relationship(User, backref='person')

    def __str__(self):
        return f'Person {self.id}, user {self.user_id})'


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


def download_user_data(user_id, name, surname, age, city):
    if not db.query(User).filter(User.id == user_id).all():
        db.add(User(id=user_id, name=name, surname=surname, age=age, city=city))
        db.commit()
        db.close()


def download_person_data(user_id, person_id, name, surname):
    db.add(Person(user_id=user_id, id=person_id, name=name, surname=surname))
    db.commit()
    db.close()


def check_person_data(user_id, person_id):
    if db.query(Person).filter(Person.id == person_id).filter(Person.user_id == user_id).all():
        db.close()
        return True
    db.close()
    return False
