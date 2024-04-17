from functools import cache
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes

@cache
def create_resource(name: str, version: str) -> Resource:
    return Resource.create(
        {
            ResourceAttributes.SERVICE_NAME: name,
            ResourceAttributes.SERVICE_VERSION: version,
        }
    )