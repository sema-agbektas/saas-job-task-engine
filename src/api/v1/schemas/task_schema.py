from pydantic import BaseModel
from uuid import UUID
from typing import Any,Dict
class CreateTaskRequest(BaseModel):
    title: str 
    payload:Dict[str,Any] 