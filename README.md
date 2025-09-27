# CodeCodex Relay Server

This project provides a lightweight RESTful relay server implemented with [FastAPI](https://fastapi.tiangolo.com/). The service acts as a controlled proxy that forwards incoming HTTP requests to pre-configured upstream services.

## Features

- **Service allow-list** – Only upstream services defined in configuration can be targeted.
- **Flexible payloads** – Supports JSON or raw body content as well as arbitrary headers and query parameters.
- **Timeout controls** – Callers can specify a per-request timeout (capped at 60 seconds).
- **Health and discovery endpoints** – Includes `/health` and `/services` routes for monitoring and configuration discovery.

## Getting Started

### Prerequisites

- Python 3.10+
- Recommended: a virtual environment (via `python -m venv .venv`)

### Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Running the Server

```bash
uvicorn app.main:app --reload
```

The service will start on `http://127.0.0.1:8000` by default.

### Configuration

Upstream services are defined through the `RELAY_RELAY_SERVICES` environment variable (or `.env` file) as either JSON or comma-separated `name=url` pairs.

Examples:

```bash
export RELAY_RELAY_SERVICES='{"httpbin": "https://httpbin.org"}'
# or
export RELAY_RELAY_SERVICES='httpbin=https://httpbin.org,service2=https://example.com'
```

### Example Request

Relay a GET request to the `/uuid` endpoint on `https://httpbin.org`:

```bash
curl -X POST http://127.0.0.1:8000/relay \
  -H "Content-Type: application/json" \
  -d '{
    "service": "httpbin",
    "path": "/uuid",
    "method": "GET"
  }'
```

Or use the convenience GET endpoint:

```bash
curl http://127.0.0.1:8000/relay/httpbin/uuid
```

## Development

- Format and lint using your preferred tools (e.g., `ruff`, `black`).
- Run the server locally via `uvicorn app.main:app --reload`.
- Extend `app/schemas.py` if additional validation rules are required.

## License

This project is provided as-is for demonstration purposes.
