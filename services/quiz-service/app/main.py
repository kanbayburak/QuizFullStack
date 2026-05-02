import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from sqlalchemy import text

from app.api.v1.router import api_router
from app.bootstrap.admin_user import seed_bootstrap_admin
from app.bootstrap.seed import seed_default_categories
from app.bootstrap.ownership_migration import ensure_ownership_columns
from app.bootstrap.user_role_migration import ensure_user_role_column
from app.core.config import get_settings
from app.core.error_handlers import register_exception_handlers
from app.db.session import async_session_factory, engine, init_db
from app.middleware.request_logging import RequestLoggingMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("quiz.main")

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    await ensure_user_role_column(engine)
    await ensure_ownership_columns(engine)
    if settings.environment == "production" and "dev-only" in settings.jwt_secret:
        logger.warning(
            "JWT_SECRET varsayılan değerde; production için güçlü bir sırrı .env ile ayarlayın.",
        )
    async with async_session_factory() as session:
        await seed_default_categories(session)
        await seed_bootstrap_admin(session)
    yield


_SWAGGER_HINT = (
    "\n\n---\n"
    "**Swagger /docs:** Korumalı uçlar (`POST`/`PATCH`/`DELETE` …) için tarayıcıda **Authorize** (kilit) "
    "düğmesine tıklayıp `POST /auth/login` yanıtındaki **`access_token`** değerini yapıştırın; "
    "`Bearer ` yazmanız gerekmez. Web panelinde giriş yapmak buraya token **eklemez** — her dokümantasyon "
    "oturumu ayrıdır.\n\n"
    "**Sorun giderme:** Token çalışıyor mu diye önce **`GET /auth/me`** deneyin. Dokümantasyon adresi ile "
    "login yaptığınız adres aynı olsun (`localhost` ile `127.0.0.1` farklı köken sayılır). İsterseniz Authorize "
    "içinde **Logout** deyip tokenı yeniden yapıştırın."
)

app = FastAPI(
    title=settings.app_name,
    description=(
        "Quiz API — kayıt (/auth/register) ve giriş (/auth/login). İçerik yazma: oturum açmış kullanıcı."
        + _SWAGGER_HINT
    ),
    version="1.0.0",
    lifespan=lifespan,
    swagger_ui_parameters={"persistAuthorization": True},
    # Slash yönlendirmesi bazı istemcilerde Authorization başlığını düşürebilir (Swagger dahil).
    redirect_slashes=False,
)


def custom_openapi() -> dict:
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    schemes = openapi_schema.setdefault("components", {}).setdefault("securitySchemes", {})
    for scheme in schemes.values():
        if isinstance(scheme, dict) and scheme.get("type") == "http" and scheme.get("scheme") == "bearer":
            scheme.setdefault(
                "description",
                "`POST /api/v1/auth/login` → `access_token`. Authorize alanına yalnızca token string'i.",
            )
            break
    else:
        schemes["HTTPBearer"] = {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "`POST /api/v1/auth/login` → `access_token`. Authorize alanına yalnızca token string'i.",
        }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi  # type: ignore[method-assign]

register_exception_handlers(app)

_origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
if settings.cors_origins == "*" or not _origins:
    _cors = ["*"]
else:
    _cors = _origins

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name, "environment": settings.environment}


@app.get("/ready")
async def ready() -> dict[str, str]:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as exc:
        logger.warning("readiness_check_failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=503, detail="Veritabanına bağlanılamıyor.") from exc
    return {"status": "ready", "service": settings.app_name}
