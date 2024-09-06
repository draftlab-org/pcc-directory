import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor

SIGNOZ_ADDR = os.getenv("SIGNOZ_ADDR")
OTEL_EXPORTER_OTLP_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")


def post_fork(server, worker):
    print(f"post_fork\nendpoint: {OTEL_EXPORTER_OTLP_ENDPOINT}\n")
    server.log.info("Worker spawned (pid: %s)", worker.pid)
    resource = Resource.create(attributes={
        "service.name": "pcc-platform-coop-directory",
        "service.namespace": os.getenv("ENV", "dev"),
    })
    provider = TracerProvider(resource=resource)

    trace.set_tracer_provider(provider)
    otlp_span_processor = BatchSpanProcessor(OTLPSpanExporter(
        endpoint=os.environ.get('OTEL_EXPORTER_OTLP_ENDPOINT')
    ))
    console_span_processor = BatchSpanProcessor(ConsoleSpanExporter(
        endpoint=os.environ.get('OTEL_EXPORTER_OTLP_ENDPOINT')
    ))

    trace.get_tracer_provider().add_span_processor(console_span_processor)
    trace.get_tracer_provider().add_span_processor(otlp_span_processor)

    LoggingInstrumentor().instrument(set_logging_format=True)
    DjangoInstrumentor().instrument(is_sql_commentor_enabled=True)
    Psycopg2Instrumentor().instrument(skip_dep_check=True, enable_commenter=True)
    RequestsInstrumentor().instrument()
