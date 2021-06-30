from typing import NamedTuple, Dict, Type, Any
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from wtforms_sqlalchemy.orm import model_form
from dataclasses import dataclass


Base = declarative_base()


class Model(NamedTuple):
    cls: Any
    edit_form: Any
    add_form: Any


class Registry(Dict[str, Model]):

    def register(self, name):
        def model_registration(model):
            self[name] = Model(
                cls=model,
                edit_form=model_form(
                    model,
                    exclude_pk=True
                ),
                add_form=model_form(
                    model,
                    exclude_pk=True
                )
            )
            return model
        return model_registration

    def create_all(self, sqlutil):
        with sqlutil.session() as session:
            for name, model in self.items():
                if model.cls.metadata.bind is None:
                    model.cls.metadata.bind = sqlutil.engine
                    model.cls.metadata.create_all()


registry = Registry()


@registry.register('user')
@dataclass
class User(Base):
    __tablename__ = 'users'

    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(50))

    def __repr__(self):
        return "User(%d, '%s')" % (self.id, self.name)
