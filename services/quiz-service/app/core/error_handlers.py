import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.config import get_settings

logger = logging.getLogger("quiz.errors")


def register_exception_handlers(app: FastAPI) -> None:
    settings = get_settings()

    @app.exception_handler(RequestValidationError)
    async def validation_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": exc.errors(), "error": "validation_error"})

    @app.exception_handler(Exception)
    async def unhandled_handler(request: Request, exc: Exception) -> JSONResponse:
        rid = getattr(request.state, "request_id", None)
        logger.exception("unhandled_error request_id=%s", rid)
        if settings.environment == "production":
            msg = "Beklenmeyen bir sunucu hatası oluştu."
        else:
            msg = str(exc)
        body: dict = {"detail": msg, "error": "internal_error"}
        if rid:
            body["request_id"] = rid
        return JSONResponse(status_code=500, content=body)
