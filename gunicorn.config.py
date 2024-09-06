import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor

SIGNOZ_ADDR = os.getenv("SIGNOZ_ADDR")


def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

    resource = Resource.create(attributes={
        "service.name": "pcc-platform-coop-directory",
        "service.namespace": os.getenv("ENV", "dev"),
    })

    trace.set_tracer_provider(TracerProvider(resource=resource))
    span_processor = BatchSpanProcessor(
        OTLPSpanExporter(endpoint=os.environ.get('OTEL_EXPORTER_OTLP_ENDPOINT'))
    )
    trace.get_tracer_provider().add_span_processor(span_processor)

    Psycopg2Instrumentor().instrument()
