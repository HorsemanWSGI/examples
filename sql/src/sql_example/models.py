from dataclasses import dataclass, asdict
from typing import Dict, Any, NamedTuple
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from alchemyjsonschema import (
    SchemaFactory, NoForeignKeyWalker, ForeignKeyWalker, StructuralWalker)


Base = declarative_base()


class Schema(NamedTuple):
    basic: Dict
    relational: Dict
    structural: Dict

    @classmethod
    def from_model(cls, model):
        return cls(
            SchemaFactory(NoForeignKeyWalker)(model),
            SchemaFactory(ForeignKeyWalker)(model),
            SchemaFactory(StructuralWalker)(model)
        )


class Registry:

    _schemas: Dict[str, Schema]
    _models: Dict[str, Any]

    def __init__(self):
        self._schemas = {}
        self._models = {}

    def register(self, name):
        def model_registration(model):
            self._models[name] = model
            self._schemas[name] = Schema.from_model(model)
            return model
        return model_registration

    def unregister(self, name):
        del self._models[name]
        del self._schemas[name]

    def __getitem__(self, name: str):
        return self._models[name]

    def get(self, name: str, default: Any):
        return self._models.get(name, default)

    def get_schema(self, name):
        return self._schemas[name]

    def create_all(self, sqlutil):
        with sqlutil.session():
            for name, model in self._models.items():
                if model.metadata.bind is None:
                    model.metadata.bind = sqlutil.engine
                    model.metadata.create_all()


registry = Registry()


@registry.register('user')
@dataclass
class User(Base):

    __tablename__ = 'users'

    id: str = Column('id', Integer, primary_key=True)
    name: str = Column('name', String(50))

    def __repr__(self):
        return f"User({self.id}, {self.name!r})"

    def dict(self):
        return asdict(self)
