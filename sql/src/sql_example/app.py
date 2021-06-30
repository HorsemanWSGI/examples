from dataclasses import dataclass, field
from typing import Type

import horseman.meta
import horseman.response
from roughrider.routing.route import Routes
from roughrider.routing.components import RoutingNode

from sql_example.request import Request



class Models(dict):

    def register(self, name):
        def model_registration(model):
            self[name] = model
            return model
        return model_registration

    def create_all(self, sqlutil):
        with sqlutil.session() as session:
            for name, model in self.items():
                if model.metadata.bind is None:
                    model.metadata.bind = sqlutil.engine
                    model.metadata.create_all()


@dataclass
class Application(RoutingNode):

    routes: Routes = field(default_factory=Routes)
    request_factory: Type[horseman.meta.Overhead] = Request
    utilities: dict = field(default_factory=dict)
    models: dict = field(default_factory=Models)

    def resolve(self, path: str, environ: dict):
        route = self.routes.match_method(path, environ['REQUEST_METHOD'])
        if route is not None:
            SQLEngine = self.utilities['sql_engine']
            with SQLEngine.session(environ) as sql_session:
                request = self.request_factory(
                    self, environ, sql_session, route)
                return route.endpoint(request, **route.params)


app = Application()


def app_with_utilities(**utilities):
    app.utilities.update(utilities)
    return app


@app.route('/')
def index(request: Request):
    users = request.sql_session.query(request.app.models['user']).all()
    return horseman.response.Response.to_json(200, {"users": users})
