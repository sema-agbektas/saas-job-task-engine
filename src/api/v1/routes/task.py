from fastapi import APIRouter, Depends,Header
from uuid import UUID
from src.api.v1.schemas.task_schema import CreateTaskRequest
from src.core.dependencies import get_repository, get_create_task, get_current_user
from src.application.use_cases.get_task_status import GetTaskStatus
from src.application.use_cases.cancel_task import CancelTask
from src.application.use_cases.list_tasks import ListTasks

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/")
async def create_task(request: CreateTaskRequest, use_case=Depends(get_create_task), current_user=Depends(get_current_user),   idempotency_key: str = Header(...)):
    task = await use_case.execute(request.title, current_user.id, request.payload,idempotency_key)
    return task

@router.get("/")
async def list_tasks(limit:int=20,offset:int=0,repository=Depends(get_repository),current_user=Depends(get_current_user)):
    use_case = ListTasks(repository)
    return await use_case.execute(current_user,limit,offset)

@router.get("/{task_id}")
async def get_task_status(task_id: UUID, repository=Depends(get_repository),current_user=Depends(get_current_user)):
    use_case = GetTaskStatus(repository)
    task = await use_case.execute(task_id,current_user)
    return task


@router.delete("/{task_id}")
async def cancel_task(task_id: UUID, repository=Depends(get_repository),current_user=Depends(get_current_user)):
    use_case = CancelTask(repository)
    task = await use_case.execute(task_id,current_user)
    return task
