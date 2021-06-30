from typing import Type, Optional, Mapping, NamedTuple
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm.query import Query
from sqlalchemy.orm import sessionmaker, scoped_session


TWO_PHASED = frozenset(('postgre', 'postgresql', 'mysql'))


class SQLAlchemyEngine(NamedTuple):
    name: str
    engine: Engine
    factory: sessionmaker

    @classmethod
    def from_url(cls, name: str,
                 url: str,
                 convert_unicode: bool = True,
                 two_phase: Optional[bool] = None,
                 query_cls: Type[Query] = Query):
        engine = create_engine(url, convert_unicode=convert_unicode)
        if two_phase is None:
            two_phase = engine.engine.dialect.name in TWO_PHASED
        elif two_phase is True and engine.dialect.name not in TWO_PHASED:
            raise ValueError(
                f'SQL Engine {engine.name} : {engine.dialect.name} '
                'does not support two phase commits'
            )
        else:
            two_phase = bool(two_phase)
        return cls(
            name=name,
            engine=engine,
            factory=sessionmaker(
                bind=engine,
                twophase=two_phase,
                query_cls=query_cls
            )
        )

    @contextmanager
    def session(self, environ: Optional[Mapping] = None):
        session = scoped_session(self.factory)
        try:
            if environ is not None:
                environ[f'sql.{self.name}'] = session
            yield session
            print('Commiting session')
            session.commit()
        except:
            print('An error occured !')
            session.rollback()
            raise
        finally:
            print('Closing session')
            session.flush()
            session.close()
            if environ is not None:
                del environ[f'sql.{self.name}']
