import weakref
from apispec import APISpec, BasePlugin
from apispec.yaml_utils import load_operations_from_docstring


class DocPlugin(BasePlugin):

    def operation_helper(self, operations, func, **kwargs):
        doc_operations = load_operations_from_docstring(func.__doc__)
        operations.update(doc_operations)


def openapi(spec: APISpec, **schemas):
    for name, schema in schemas:
        spec.components.schema(name, schema=schema)
    def openapi_wrapper(func):
        func.__openapi__ = load_operations_from_docstring(func.__doc__)
        func.__spec__ = weakref.ref(spec)
        return func
    return openapi_wrapper


spec = APISpec(
    title="SQL Example",
    version="1.0.0",
    openapi_version="3.0.2",
    plugins=[DocPlugin()]
)
