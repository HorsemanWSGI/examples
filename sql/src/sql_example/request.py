import horseman.parsers
from horseman.http import Query, Cookies, ContentType
from roughrider.routing.components import RoutingRequest


class Request(RoutingRequest):

    __slots__ = (
        '_data'
        'app',
        'cookies',
        'query',
        'content_type',
        'environ',
        'method',
        'route',
        'sql_session',
    )

    def __init__(self, app, environ, sql_session, route):
        self._data = ...
        self.app = app
        self.environ = environ
        self.method = environ['REQUEST_METHOD'].upper()
        self.route = route
        self.query = Query.from_environ(environ)
        self.cookies = Cookies.from_environ(environ)
        self.sql_session = sql_session
        if 'CONTENT_TYPE' in self.environ:
            self.content_type = ContentType.from_http_header(
                self.environ['CONTENT_TYPE'])
        else:
            self.content_type = None

    def set_data(self, data):
        self._data = data

    def get_data(self):
        return self._data

    def extract(self):
        if self._data is not ...:
            return self.get_data()

        if self.content_type:
            self.set_data(horseman.parsers.parser(
                self.environ['wsgi.input'], self.content_type))

        return self.get_data()
