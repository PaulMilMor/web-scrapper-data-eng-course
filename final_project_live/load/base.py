from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# The above code is creating a database engine, a session, and a base.
Engine = create_engine('sqlite:///newspapers.db')

Session = sessionmaker(bind=Engine)

Base = declarative_base()