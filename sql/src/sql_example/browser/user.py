import horseman.response
import json
from functools import partial
from sql_example.app import routes
from sql_example.browser import AddForm, EditForm, TEMPLATES
from sql_example import models
from sql_example.request import Request
from roughrider.predicate.errors import HTTPConstraintError
from roughrider.predicate.decorator import with_predicates
import jsonschema


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


@routes.register('/new')
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


def error_to_response(error: HTTPConstraintError):
    return horseman.response.Response.to_json(
        error.status, body={'error': error.message})


def json_only(request: Request):
    if (not request.content_type or
        request.content_type.mimetype != 'application/json'):
        raise HTTPConstraintError(
            status=406, message='Expected content-type: application/json')


def jsonschema_validator(modelname: str):
    def validate_schema(request: Request):
        data = request.extract()
        schema = models.registry.get_schema(modelname)
        try:
            jsonschema.validate(instance=data.json, schema=schema.basic)
        except jsonschema.exceptions.ValidationError as err:
            raise HTTPConstraintError(status=400, message=err.message)
    return validate_schema


@routes.register('/api/new', methods=['PUT'])
@with_predicates(
    [
        json_only,
        jsonschema_validator('user')
    ],
    handler=error_to_response
)
def new_user(request: Request):
    data = request.extract()
    model = models.registry['user']
    obj = model(**data.json)
    request.sql_session.add(obj)
    return horseman.response.Response(201)
