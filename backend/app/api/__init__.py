from fastapi import APIRouter
from . import webhook, auth, conversations, stats

router = APIRouter()
router.include_router(webhook.router, prefix="/webhook", tags=["webhook"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
router.include_router(stats.router, prefix="/stats", tags=["stats"])