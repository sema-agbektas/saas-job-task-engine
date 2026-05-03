from fastapi import FastAPI
from src.api.v1.routes.task import router
app= FastAPI(title="SaaS Job & Task Engine", version="1.0.0")
app.include_router(router)