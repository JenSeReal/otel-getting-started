from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor
from opentelemetry import trace as trace_api
from opentelemetry.sdk.trace import TracerProvider
from resource_utils import create_resource

def create_tracing_pipeline() -> BatchSpanProcessor:
    console_exporter = ConsoleSpanExporter()
    span_processor = BatchSpanProcessor(console_exporter)
    return span_processor


def create_tracer(name: str, version: str) -> trace_api.Tracer:
    provider = TracerProvider(resource=create_resource(name, version))
    provider.add_span_processor(create_tracing_pipeline())
    trace_api.set_tracer_provider(provider)
    tracer = trace_api.get_tracer(name, version)
    return tracer