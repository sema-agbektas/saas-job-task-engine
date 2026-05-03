from pydantic import BaseModel
from uuid import UUID
from typing import Any,Dict
class CreateTaskRequest(BaseModel):
    title: str 
    user_id:UUID 
    payload:Dict[str,Any] 