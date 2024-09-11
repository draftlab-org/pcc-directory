import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor

OTEL_EXPORTER_OTLP_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")


def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

    otlp_span_processor = BatchSpanProcessor(OTLPSpanExporter())

    trace.get_tracer_provider().add_span_processor(otlp_span_processor)

    LoggingInstrumentor().instrument()
    DjangoInstrumentor().instrument()
    Psycopg2Instrumentor().instrument(skip_dep_check=True)
