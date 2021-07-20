from dataclasses import dataclass, asdict
from typing import Dict, Any, NamedTuple, Type
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from alchemyjsonschema import (
    SchemaFactory, NoForeignKeyWalker, ForeignKeyWalker, StructuralWalker)


Base = declarative_base()


def create_sql_tables(sqlutil):
    with sqlutil.session():
        Base.metadata.bind = sqlutil.engine
        Base.metadata.create_all()


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


def jsonschema(model: Type[Base]) -> Schema:
    if schema := getattr(model, '__jsonschema__', None):
        return schema
    schema = model.__jsonschema__ = Schema.from_model(model)
    return schema


@dataclass
class User(Base):

    __tablename__ = 'users'

    id: str = Column('id', Integer, primary_key=True)
    name: str = Column('name', String(50))

    def __repr__(self):
        return f"User({self.id}, {self.name!r})"

    def dict(self):
        return asdict(self)
