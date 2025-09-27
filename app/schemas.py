"""Pydantic schemas for the relay API."""
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, HttpUrl, root_validator


class HTTPMethod(str, Enum):
    """Supported HTTP methods for relay requests."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class RelayRequest(BaseModel):
    """Incoming request payload instructing the relay server."""

    service: str = Field(..., description="Service identifier configured on the server")
    path: str = Field(
        "/",
        description="Path appended to the upstream service base URL",
        regex=r"^/",
    )
    method: HTTPMethod = Field(HTTPMethod.GET, description="HTTP method to relay")
    query_params: Optional[Dict[str, str]] = Field(
        default=None,
        description="Query parameters to include on the forwarded request",
    )
    headers: Optional[Dict[str, str]] = Field(
        default=None,
        description="Optional headers to include when relaying the request",
    )
    json_body: Optional[Any] = Field(
        default=None,
        description="JSON body content to send upstream (mutually exclusive with raw_body)",
    )
    raw_body: Optional[str] = Field(
        default=None,
        description="Raw string payload to send upstream when JSON is not desired",
    )
    timeout: float = Field(10.0, gt=0, le=60, description="Timeout in seconds for the upstream request")

    class Config:
        anystr_strip_whitespace = True

    @root_validator
    def _ensure_single_body(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        json_body = values.get("json_body")
        raw_body = values.get("raw_body")
        if json_body is not None and raw_body is not None:
            raise ValueError("Only one of json_body or raw_body can be supplied")
        return values


class RelayResponse(BaseModel):
    """Response payload returned to the caller after relaying the request."""

    status_code: int = Field(..., description="HTTP status code from the upstream service")
    headers: Dict[str, str] = Field(
        default_factory=dict,
        description="Headers returned by the upstream service",
    )
    body: Optional[Any] = Field(
        default=None,
        description="Parsed JSON body returned by the upstream service, if available",
    )
    text: Optional[str] = Field(
        default=None,
        description="Raw text body returned by the upstream service when JSON parsing fails",
    )
    elapsed_ms: float = Field(
        ...,
        description="Time spent communicating with the upstream service, in milliseconds",
    )
    url: HttpUrl = Field(
        ..., description="The full URL that was called on the upstream service"
    )
