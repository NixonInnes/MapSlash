from yaml import safe_load
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

engine = create_engine('sqlite:///db.sqlite')

Session = sessionmaker(bind=engine)
session = scoped_session(Session)

with open('config.yml', 'r') as f:
    config = safe_load(f)