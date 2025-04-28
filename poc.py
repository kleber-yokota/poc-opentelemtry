import time
import random
import logging
import psutil
import sympy

from opentelemetry import trace, metrics, _logs
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.trace import Status, StatusCode
from opentelemetry.metrics import Observation, CallbackOptions

# Logging setup
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("etl-otel")

# OpenTelemetry logs
log_exporter = OTLPLogExporter(endpoint="http://localhost:4317", insecure=True)
log_processor = BatchLogRecordProcessor(log_exporter)
log_provider = LoggerProvider()
log_provider.add_log_record_processor(log_processor)
_logs.set_logger_provider(log_provider)

# Attach the LoggingHandler
logger.addHandler(LoggingHandler(level=logging.DEBUG))

# Tracer setup
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer("etl-tracer")
span_processor = BatchSpanProcessor(
    OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
)
trace.get_tracer_provider().add_span_processor(span_processor)

# Metrics setup
otlp_exporter = OTLPMetricExporter(endpoint="http://localhost:4317", insecure=True)
metrics.set_meter_provider(MeterProvider(
    metric_readers=[PeriodicExportingMetricReader(
        otlp_exporter, export_interval_millis=1000
    )]
))
meter = metrics.get_meter("etl-metrics")

# CPU and RAM observation callbacks
def cpu(span_id):
    def callback(options: CallbackOptions):
        process = psutil.Process()
        cpu_percent = process.cpu_percent(interval=0.5)
        yield Observation(cpu_percent, {"process": "etl-pipeline", "span_id": span_id})
    return callback

def ram(span_id):
    def callback(options: CallbackOptions):
        process = psutil.Process()
        ram_mb = process.memory_info().rss / (1024 * 1024)
        yield Observation(ram_mb, {"process": "etl-pipeline", "span_id": span_id})
    return callback

# Define gauges
cpu_gauge = meter.create_observable_gauge(
    name="cpu_usage_percent",
    description="CPU usage per ETL step",
    unit="%",
    callbacks=[cpu("init")]
)

ram_gauge = meter.create_observable_gauge(
    name="ram_usage_mb",
    description="RAM usage per ETL step",
    unit="MB",
    callbacks=[ram("init")]
)

# Function to simulate CPU stress
def find_large_prime():
    while True:
        num = random.getrandbits(24)
        if sympy.isprime(num):
            return num

def stress_cpu(duration=4):
    start_time = time.time()
    while time.time() - start_time < duration:
        find_large_prime()

# ETL steps with logs
def extract():
    with tracer.start_as_current_span("extract") as span:
        stress_cpu()
        logger.info("Extract step completed")
        span.set_status(Status(StatusCode.OK))

def transform():
    with tracer.start_as_current_span("transform") as span:
        stress_cpu()
        logger.info("Transform step completed")
        span.set_status(Status(StatusCode.OK))

def load():
    with tracer.start_as_current_span("load") as span:
        time.sleep(random.uniform(1, 2))
        logger.info("Load step completed")
        span.set_status(Status(StatusCode.OK))

# Main loop
if __name__ == "__main__":
    with tracer.start_as_current_span("etl-full-pipeline") as parent_span:
        span_id = f"{parent_span.get_span_context().span_id:016x}"
        ram_gauge._callbacks = [ram(span_id)]
        cpu_gauge._callbacks = [cpu(span_id)]
        extract()
        transform()
        load()
