from dataclasses import dataclass, field
from typing import Type

import horseman.meta
import horseman.response
from roughrider.routing.route import Routes
from roughrider.routing.components import RoutingNode

from sql_example.request import Request


@dataclass
class Application(RoutingNode):

    routes: Routes = field(default_factory=Routes)
    request_factory: Type[horseman.meta.Overhead] = Request

    def resolve(self, path: str, environ: dict):
        route = self.routes.match_method(path, environ['REQUEST_METHOD'])
        if route is not None:
            request = self.request_factory(self, environ, route)
            return route.endpoint(request, **route.params)


app = Application()


@app.route('/')
def index(request: Request):
    return horseman.response.Response.create(200, body='Yeah')
