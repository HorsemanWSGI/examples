import horseman.response
from roughrider.cors.policy import CORSPolicy
from api import models
from api.app import routes
from api.request import Request


CORS = CORSPolicy(
    allow_headers=['Content-Type'],
    expose_headers=['Content-Type'],
    credentials=False
)


@routes.register(
    '/api/new', methods=['PUT'], cors=CORS, openapi=True,
    schemas={'user': models.jsonschema(models.User).basic}
)
def new_user(request: Request):
    """Create a new user
    ---
    put:
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
