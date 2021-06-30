from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sql_example.app import app


Base = declarative_base()


@app.models.register('user')
class User(Base):
    __tablename__ = 'users'

    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(50))

    def __repr__(self):
        return "User(%d, '%s')" % (self.id, self.name)


def creator(engine, *models):
    for model in models:
        users_engine.bind(UserBase)
