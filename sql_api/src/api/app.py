from dataclasses import dataclass, field
from typing import Type
from horseman.response import Response
from horseman.http import HTTPError
from roughrider.routing.route import NamedRoutes
from roughrider.routing.components import RoutingNode
from roughrider.sqlalchemy.component import SQLAlchemyEngine
from sql_example.request import Request


routes = NamedRoutes()

@dataclass
class Application(RoutingNode):

    sql_engine: SQLAlchemyEngine
    routes: NamedRoutes = routes
    utilities: dict = field(default_factory=dict)
    request_factory: Type[Request] = Request

    def preflight(self, path, environ):
        if environ['REQUEST_METHOD'] != 'OPTIONS':
            # This is not a preflight request.
            return None

        origin = environ.get("HTTP_ORIGIN")
        acr_method = environ.get("HTTP_ACCESS_CONTROL_REQUEST_METHOD")
        acr_headers = environ.get("HTTP_ACCESS_CONTROL_REQUEST_HEADERS")

        if origin is None or acr_method is None:
            # This is not a preflight request.
            return None

        payload, params = self.routes.match(path)
        if payload is None:
            # Route does not exist.
            raise HTTPError(404)


        if not acr_method in payload:
            # Request method does not exist.
            # Return a list of acceptable methods.
            # This could use a global CORS Policy
            methods = list(payload.keys())
            return Response(204, headers={
                'Access-Control-Allow-Methods': ', '.join(methods)})

        metadata = payload[acr_method].metadata
        if metadata is None or 'cors' not in metadata:
            # This could use a global CORS Policy
            # This is a preflight but we don't have any CORS information
            raise HTTPError(406)

        headers = metadata['cors'].preflight(
            origin, acr_method, acr_headers
        )
        # We found a CORS policy and created the headers.
        # We return a bodyless response with the infos.
        return Response(204, headers=dict(headers))

    def resolve(self, path: str, environ: dict):
        if response := self.preflight(path, environ):
            return response

        route = self.routes.match_method(path, environ['REQUEST_METHOD'])
        if route is not None:
            with self.sql_engine.session() as sql_session:
                request = self.request_factory(
                    self, environ, sql_session, route)
                return route.endpoint(request, **route.params)
