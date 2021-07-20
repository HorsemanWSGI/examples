import horseman.response
import jsonschema
from roughrider.predicate.errors import HTTPConstraintError
from api import models


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
