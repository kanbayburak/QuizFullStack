from fastapi import APIRouter

from app.api.v1 import categories, questions

api_router = APIRouter()
api_router.include_router(categories.router)
api_router.include_router(questions.router)
