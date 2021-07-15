import horseman.response
import json
from functools import partial
from sql_example.app import routes
from sql_example.browser import AddForm, EditForm, TEMPLATES
from sql_example import models
from sql_example.request import Request


@routes.register('/')
def index(request: Request):
    model = models.registry['user']
    users = request.sql_session.query(model).all()
    template = TEMPLATES['listing.pt']
    html = template.render(
        users=users,
        layout=TEMPLATES['layout.pt']
    )
    return horseman.response.Response.html(body=html)


@routes.register('/new', )
class AddUser(AddForm):
    modelname = 'user'


@routes.register('/{uid:digit}/edit')
class EditUser(EditForm):
    modelname = 'user'

    def get_context(self, request):
        return request.sql_session.query(
            self.model).get(request.route.params['uid'])


@routes.register('/{uid:digit}/view')
def view(request: Request, uid: int):
    model = models.registry['user']
    user = request.sql_session.query(model).get(uid)
    template = TEMPLATES['user.pt']
    html = template.render(
        user=user,
        format=partial(json.dumps, indent=4),
        schema=models.registry.get_schema('user'),
        layout=TEMPLATES['layout.pt']
    )
    return horseman.response.Response.html(body=html)


@routes.register('/{uid:digit}/delete')
def delete(request: Request, uid: int):
    model = models.registry['user']
    user = request.sql_session.query(model).get(uid)
    request.sql_session.delete(user)
    return horseman.response.Response.redirect('/')
