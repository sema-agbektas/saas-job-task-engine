from fastapi import FastAPI,Request
from contextlib import asynccontextmanager
import redis.asyncio as aioredis
from src.core.config import settings
from src.api.v1.routes.task import router
from src.api.v1.routes.auth import router as auth_router
from fastapi.responses import JSONResponse
from src.domain.exceptions.domain_exceptions import TaskNotFoundError

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = await aioredis.from_url(settings.REDIS_URL)
    yield
    await app.state.redis.aclose()


app = FastAPI(title="SaaS Job & Task Engine", version="1.0.0", lifespan=lifespan)
app.include_router(router)
app.include_router(auth_router)

@app.exception_handler(TaskNotFoundError)
async def task_not_found_handler(request:Request,exc:TaskNotFoundError):
    return JSONResponse(status_code=404,content={"detail":str(exc)})
@app.exception_handler(PermissionError)
async def permission_error_handler(request:Request,exc:PermissionError):
    return JSONResponse(status_code=403,content={"detail":str(exc)})