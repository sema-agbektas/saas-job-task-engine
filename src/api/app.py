from fastapi import FastAPI
from contextlib import asynccontextmanager
import redis.asyncio as aioredis
from src.core.config import settings
from src.api.v1.routes.task import router
from src.api.v1.routes.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = await aioredis.from_url(settings.REDIS_URL)
    yield
    await app.state.redis.aclose()


app = FastAPI(title="SaaS Job & Task Engine", version="1.0.0", lifespan=lifespan)
app.include_router(router)
app.include_router(auth_router)