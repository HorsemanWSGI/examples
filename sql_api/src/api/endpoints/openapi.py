import json
from horseman.response import Response
from api.app import routes


@routes.register('/openapi')
def openapi(request):
    specs = json.dumps(routes.spec.to_dict())
    return Response.from_json(body=specs.encode())
