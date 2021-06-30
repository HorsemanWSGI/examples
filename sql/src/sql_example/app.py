from dataclasses import dataclass, field
from typing import Type
from pathlib import Path

import horseman.meta
import horseman.response
from roughrider.routing.route import NamedRoutes
from roughrider.routing.components import RoutingNode
from sql_example.request import Request
from sql_example.models import Registry
from sql_example.sqlsession import SQLAlchemyEngine

from chameleon.zpt.loader import TemplateLoader


templates = TemplateLoader(str(Path(__file__).parent))
routes = NamedRoutes()


@dataclass
class Application(RoutingNode):

    sql_engine: SQLAlchemyEngine
    routes: NamedRoutes = routes
    utilities: dict = field(default_factory=dict)
    models: Registry = field(default_factory=Registry)
    request_factory: Type[horseman.meta.Overhead] = Request

    def __post_init__(self):
        self.models.create_all(self.sql_engine)

    def resolve(self, path: str, environ: dict):
        route = self.routes.match_method(path, environ['REQUEST_METHOD'])
        if route is not None:
            with self.sql_engine.session(environ) as sql_session:
                request = self.request_factory(
                    self, environ, sql_session, route)
                return route.endpoint(request, **route.params)


@routes.register('/')
def index(request: Request):
    model = request.app.models['user']
    users = request.sql_session.query(model.cls).all()
    return horseman.response.Response.to_json(200, {"users": users})


@routes.register('/new', methods=['GET', 'POST'])
def new(request: Request):
    model = request.app.models['user']
    if request.method == 'POST':
        data = request.extract()
        form = model.add_form(data.form)
        if form.validate():
            obj = model.cls()
            form.populate_obj(obj)
            request.sql_session.add(obj)
            return horseman.response.redirect('/')
    else:
        form = model.add_form()

    form_template = templates['form.pt']
    html = form_template.render(
        title='New user', action=request.route.path, form=form)
    return horseman.response.reply(
        200, body=html,
        headers={"Content-Type": "text/html; charset=utf-8"}
    )


@routes.register('/{uid:digit}/edit', methods=['GET', 'POST'])
def edit(request: Request, uid: int):
    model = request.app.models['user']
    user = request.sql_session.query(model.cls).get(uid)
    if user is None:
        return horseman.response.reply(404, body='Unknown user')

    if request.method == 'POST':
        data = request.extract()
        form = model.edit_form(data.form, obj=user)
        if form.validate():
            form.populate_obj(user)
            return horseman.response.redirect('/')
    else:
        form = model.edit_form(obj=user)

    form_template = templates['form.pt']
    html = form_template.render(
        title=f'Edit user {uid}', action=request.route.path, form=form)
    return horseman.response.reply(
        200, body=html,
        headers={"Content-Type": "text/html; charset=utf-8"}
    )
