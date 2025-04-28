
# PoC OpenTelemetry ETL Pipeline

This repository demonstrates a simple ETL (Extract, Transform, Load) pipeline instrumented with OpenTelemetry for tracing, logging, and metrics collection.

All the code explained in detail is available in the [related blog post](#) (link to be updated).

---

## Overview

The project simulates an ETL process where:

- **Extract** and **Transform** phases simulate CPU stress by searching for large prime numbers.
- **Load** phase simulates data loading with a random delay.
- CPU and RAM usage are captured and exported as metrics.
- Each ETL step is traced and logs are sent to a backend.

The telemetry data (traces, metrics, and logs) is exported using OpenTelemetry Protocol (OTLP) and visualized with Grafana, Loki, Tempo, and Mimir — easily deployed via Docker Compose.

---

## Project Structure

- `etl_pipeline.py`: The main script containing the ETL pipeline and OpenTelemetry instrumentation.
- `docker-compose.yml`: Deploys the OTEL LGTM stack (Loki, Grafana, Tempo, Mimir) locally.
- `pyproject.toml`: Project dependencies, managed using [`uv`](https://github.com/astral-sh/uv).

---

## Setup and Running

### 1. Requirements

- Python 3.11+
- [`uv`](https://github.com/astral-sh/uv) for dependency management
- Docker and Docker Compose

### 2. Install dependencies

```bash
uv pip install -r pyproject.toml
```

### 3. Start Observability Stack

```bash
docker-compose up -d
```

This will start:
- Grafana (http://localhost:3000, login: `admin` / `admin`)
- Loki (logs backend)
- Tempo (traces backend)
- Mimir (metrics backend)
- OTLP gRPC endpoint on `http://localhost:4317`

### 4. Run the ETL pipeline

```bash
python etl_pipeline.py
```

You will see logs locally, and traces/metrics/logs will be sent to the OpenTelemetry backend.

---

## Observability Details

| Aspect   | Description |
| -------- | ----------- |
| Traces   | Each ETL step (`extract`, `transform`, `load`) is a separate span. |
| Metrics  | CPU and RAM usage are observed and sent as gauges. |
| Logs     | Logs are captured for each ETL phase and linked to traces. |

Metrics and spans are dynamically tied to the current ETL operation, with `span_id` associated as a metric attribute.

---

## Dashboards and Visualization

Access Grafana at [http://localhost:3000](http://localhost:3000).

You can create dashboards to:
- View CPU and RAM usage over time.
- See traces of each ETL run.
- Analyze logs alongside traces using Grafana's "Explore" feature.

---

## Tech Stack

- **Python**: Data processing and OpenTelemetry client
- **OpenTelemetry**: Tracing, Metrics, and Logs SDK
- **Grafana LGTM Stack**: Visualization and storage backend
- **uv**: Dependency manager (fast and modern alternative to pip)

---

## License

This project is licensed under the [MIT License](LICENSE) (or adjust if needed).
