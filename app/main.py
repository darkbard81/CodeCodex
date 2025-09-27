"""FastAPI application entry point for the relay server."""
from __future__ import annotations

import logging
from typing import Any, Dict

import httpx
from fastapi import FastAPI, HTTPException

from .config import settings
from .schemas import HTTPMethod, RelayRequest, RelayResponse

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Relay API Server",
    description=(
        "A simple RESTful relay server that forwards requests to configured upstream "
        "services with optional validation and timeout controls."
    ),
    version="0.1.0",
)


@app.get("/health", tags=["system"])
async def health_check() -> Dict[str, str]:
    """Health endpoint for monitoring."""

    return {"status": "ok"}


@app.get("/services", tags=["system"])
async def list_services() -> Dict[str, Dict[str, str]]:
    """Return the configured upstream services."""

    return {"services": settings.relay_services}


async def _perform_request(payload: RelayRequest) -> RelayResponse:
    if payload.service not in settings.relay_services:
        raise HTTPException(status_code=404, detail="Unknown service requested")

    base_url = settings.relay_services[payload.service]
    headers = payload.headers or {}

    request_kwargs: Dict[str, Any] = {
        "method": payload.method.value,
        "url": payload.path,
        "params": payload.query_params,
        "headers": headers,
    }

    if payload.json_body is not None:
        request_kwargs["json"] = payload.json_body
    elif payload.raw_body is not None:
        request_kwargs["content"] = payload.raw_body

    timeout = httpx.Timeout(payload.timeout)

    async with httpx.AsyncClient(base_url=base_url, timeout=timeout) as client:
        try:
            response = await client.request(**request_kwargs)
        except httpx.TimeoutException as exc:
            logger.warning("Timeout when calling %s%s", base_url, payload.path)
            raise HTTPException(status_code=504, detail=str(exc)) from exc
        except httpx.HTTPError as exc:
            logger.exception("Error when calling upstream service")
            raise HTTPException(status_code=502, detail=str(exc)) from exc

    parsed_body: Any = None
    raw_text: str | None = None

    try:
        parsed_body = response.json()
    except ValueError:
        raw_text = response.text

    return RelayResponse(
        status_code=response.status_code,
        headers=dict(response.headers),
        body=parsed_body,
        text=raw_text,
        elapsed_ms=response.elapsed.total_seconds() * 1000,
        url=response.url,
    )


@app.post("/relay", response_model=RelayResponse, tags=["relay"])
async def relay(payload: RelayRequest) -> RelayResponse:
    """Relay the incoming request to the configured upstream service."""

    return await _perform_request(payload)


@app.get("/relay/{service}/{path:path}", response_model=RelayResponse, tags=["relay"])
async def relay_get(service: str, path: str) -> RelayResponse:
    """Convenience GET endpoint using path parameters."""

    payload = RelayRequest(service=service, path="/" + path, method=HTTPMethod.GET)
    return await _perform_request(payload)
