from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings

settings = get_settings()
_http: httpx.AsyncClient | None = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    global _http
    _http = httpx.AsyncClient(base_url=settings.quiz_service_url.rstrip("/"), timeout=60.0)
    yield
    await _http.aclose()
    _http = None


app = FastAPI(title=settings.app_name, lifespan=lifespan)

_origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


@app.api_route("/api/v1/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD"])
async def proxy_to_quiz(path: str, request: Request) -> Response:
    assert _http is not None
    url = f"/api/v1/{path}"
    if request.url.query:
        url = f"{url}?{request.url.query}"
    body = await request.body()
    fwd_headers = {}
    ct = request.headers.get("content-type")
    if ct:
        fwd_headers["content-type"] = ct
    auth = request.headers.get("authorization")
    if auth:
        fwd_headers["authorization"] = auth

    r = await _http.request(
        request.method,
        url,
        content=body if body else None,
        headers=fwd_headers,
    )
    out_headers = {
        k: v
        for k, v in r.headers.items()
        if k.lower() in ("content-type", "content-length") or k.lower().startswith("x-")
    }
    return Response(content=r.content, status_code=r.status_code, headers=out_headers)
