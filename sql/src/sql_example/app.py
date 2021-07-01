from dataclasses import dataclass, field
from typing import Type

from roughrider.routing.route import NamedRoutes
from roughrider.routing.components import RoutingNode
from roughrider.sqlalchemy.component import SQLAlchemyEngine
from sql_example.request import Request
from sql_example.models import Registry


routes = NamedRoutes()


@dataclass
class Application(RoutingNode):

    sql_engine: SQLAlchemyEngine
    routes: NamedRoutes = routes
    utilities: dict = field(default_factory=dict)
    models: Registry = field(default_factory=Registry)
    request_factory: Type[Request] = Request

    def __post_init__(self):
        self.models.create_all(self.sql_engine)

    def resolve(self, path: str, environ: dict):
        route = self.routes.match_method(path, environ['REQUEST_METHOD'])
        if route is not None:
            with self.sql_engine.session() as sql_session:
                request = self.request_factory(
                    self, environ, sql_session, route)
                return route.endpoint(request, **route.params)
