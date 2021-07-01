from dataclasses import dataclass
from typing import Dict, Any
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Registry(Dict[str, Any]):

    def register(self, name):
        def model_registration(model):
            self[name] = model
            return model
        return model_registration

    def create_all(self, sqlutil):
        with sqlutil.session():
            for name, model in self.items():
                if model.metadata.bind is None:
                    model.metadata.bind = sqlutil.engine
                    model.metadata.create_all()


registry = Registry()


@registry.register('user')
@dataclass
class User(Base):
    __tablename__ = 'users'

    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(50))

    def __repr__(self):
        return "User(%d, '%s')" % (self.id, self.name)
