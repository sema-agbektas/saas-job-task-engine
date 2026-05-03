from fastapi import APIRouter
from src.api.v1.schemas.task_schema import CreateTaskRequest
from src.core.dependencies import get_repository,get_create_task
from fastapi import Depends
from uuid import UUID
from src.application.use_cases.get_task_status import GetTaskStatus
from src.application.use_cases.cancel_task import CancelTask
router=APIRouter(prefix="/tasks",tags=["tasks"])


@router.post("/")
async def create_task(request: CreateTaskRequest, use_case=Depends(get_create_task)):
    task = await use_case.execute(request.title, request.user_id, request.payload)
    return task

@router.get("/{task_id}")
async def get_task_status(task_id:UUID,repository=Depends(get_repository)):
    use_case=GetTaskStatus(repository)
    task=await use_case.execute(task_id)
    return task

@router.delete("/{task_id}")
async def cancel_task(task_id:UUID,repository=Depends(get_repository)):
    use_case=CancelTask(repository)
    task=await use_case.execute(task_id)
    return task