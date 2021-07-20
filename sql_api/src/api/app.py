import logging
from dataclasses import dataclass, field
from typing import Type
from horseman.response import Response
from horseman.http import HTTPError
from roughrider.routing.route import Routes, RouteEndpoint, HTTPMethods
from roughrider.routing.components import RoutingNode
from roughrider.sqlalchemy.component import SQLAlchemyEngine
from api.request import Request
from roughrider.cors.policy import CORSPolicy
from apispec import APISpec
from apispec.yaml_utils import load_operations_from_docstring


class APIRoutes(Routes):

    def __init__(self, spec, *args, **kwargs):
        self.spec = spec
        super().__init__(*args, **kwargs)

    def register(self, path: str, methods: HTTPMethods = None, **metadata):
        openapi = bool(metadata.pop('openapi', False))
        schemas = metadata.pop('schemas', None)
        if schemas:
            if not openapi:
                logging.warning(
                    f"Route {path!r}: schemas can only be registered "
                    "if your route is openapi-enabled."
                )
            else:
                for name, schema in schemas.items():
                    if not name in self.spec.components.schemas:
                        self.spec.components.schema(name, schema)
        def routing(view):
            operations = {} if openapi else None
            for endpoint, verbs in self.extractor(view, methods):
                if operations is not None:
                    ops = load_operations_from_docstring(endpoint.__doc__)
                    if ops:
                        undefined = set(ops.keys()) - set(
                            (v.lower() for v in verbs))
                        if undefined:
                            logging.warning(
                                f"Route {path!r}: openapi is missing "
                                f"def(s) for : {', '.join(undefined)}."
                            )
                        operations.update(ops)

                self.add(path, {
                    method: RouteEndpoint(
                        endpoint=endpoint,
                        method=method,
                        metadata=metadata or None
                    ) for method in verbs
                })

            if operations is not None:
                self.spec.path(path=path, operations=operations)
            return view
        return routing


routes = APIRoutes(spec=APISpec(
    title="SQL Example",
    version="1.0.0",
    openapi_version="3.0.2"
))


@dataclass
class Application(RoutingNode):

    sql_engine: SQLAlchemyEngine
    routes: Routes = routes
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
