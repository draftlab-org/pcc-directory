import os

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor

SIGNOZ_ADDR = os.getenv("SIGNOZ_ADDR")

resource = Resource.create({
    "service.name": "portal-coopersystem",
    "service.namespace": os.getenv("ENV", "dev"),
})

provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)

otlp_exporter = OTLPSpanExporter(endpoint=f"{SIGNOZ_ADDR}:4317", insecure=True)
span_processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(span_processor)

DjangoInstrumentor().instrument()
