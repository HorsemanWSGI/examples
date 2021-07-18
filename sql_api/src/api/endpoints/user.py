import horseman.response
import jsonschema
from functools import partial
from roughrider.cors.policy import CORSPolicy
from roughrider.predicate.decorator import with_predicates
from roughrider.predicate.errors import HTTPConstraintError
from api import models, routes
from api.openapi import spec, openapi
from api.request import Request


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



CORS = CORSPolicy(
    allow_headers=['Content-Type'],
    expose_headers=['Content-Type'],
    credentials=False
)


@routes.register('/api/new', methods=['PUT'], cors=CORS)
# @with_predicates(
#     [
#         json_only,
#         jsonschema_validator('user')
#     ],
#     handler=error_to_response
# )
@openapi(spec, user=models.jsonschema(models.User).basic)
def new_user(request: Request):
    """Create a new user
    ---
    description: Create a new user

    requestBody:
      required: true
      content:
        application/json:
          schema: {$ref: '#/definitions/User'}
    responses:
      201:
        description: The user was created successfully.
      400:
        description: The request content was incorrect.
    """
    data = request.extract()
    model = models.registry['user']
    obj = model(**data.json)
    request.sql_session.add(obj)
    return horseman.response.Response(201)
