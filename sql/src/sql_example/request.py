import horseman.parsing
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
    )

    def __init__(self, app, environ, route):
        self._data = ...
        self.app = app
        self.environ = environ
        self.method = environ['REQUEST_METHOD'].upper()
        self.route = route
        self.query = Query.from_environ(environ)
        self.cookies = Cookies.from_environ(environ)
        if 'CONTENT_TYPE' in self.environ:
            ct = self.environ['CONTENT_TYPE']
            self.content_type = ContentType(ct, *cgi.parse_header(ct))
        else:
            self.content_type = None

    def set_data(self, data):
        self._data = data

    def get_data(self):
        return self._data

    def extract(self):
        if self._data is not ...:
            return self.get_data()

        if content_type := self.content_type:
            self.set_data(horseman.parsing.parse(
                self.environ['wsgi.input'], content_type.raw))

        return self.get_data()
