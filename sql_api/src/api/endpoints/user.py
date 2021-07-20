import horseman.response
from roughrider.cors.policy import CORSPolicy
from api import models
from api.app import routes
from api.request import Request
from horseman.meta import APIView


CORS = CORSPolicy(
    allow_headers=['Content-Type'],
    expose_headers=['Content-Type'],
    credentials=False
)

@routes.register(
    '/api/newuser', cors=CORS, openapi=True,
    schemas={'user': models.jsonschema(models.User).basic}
)
class CreateUser(APIView):

    def PUT(self, request: Request):
        """Create a new user
        ---
        put:
          description: Create a new user

          requestBody:
            required: true
            content:
              application/json:
                schema: {$ref: '#/definitions/user'}
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

    def POST(self, request: Request):
        """Create a new user
        ---
        post:
          description: Create a new user

          requestBody:
            required: true
            content:
              application/json:
                schema: {$ref: '#/definitions/user'}
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


@routes.register(
    '/api/user', cors=CORS, openapi=True,
    schemas={'user': models.jsonschema(models.User).basic}
)
def get_user(request: Request):
    """Get a user
    ---
    get:
      description: Get user info

      responses:
        200:
          description: The user was created successfully.
          content:
            application/json:
              schema: {$ref: '#/definitions/user'}
        400:
          description: The request content was incorrect.
    """
    return horseman.response.Response(200)
