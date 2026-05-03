from dataclasses import dataclass,field
from datetime import datetime,UTC
from typing import Any,Dict
from uuid import UUID,uuid4
from src.domain.enums.task_status import TaskStatus
@dataclass
class Task:
    """task entiysi projedeki iş birimlerini temsil eder"""
    
    title: str #görevin kısa başlığı
    user_id:UUID #görevi oluşturan kullanıcının benzersiz kimliği
    payload:Dict[str,Any] #görevle ilgili teknik detaylar
    #otomatik olarak her göreve benzersiz bir UUID atar
    id: UUID = field(default_factory=uuid4)
    #oluşturlan her görev opending beklmede başlar
    status: TaskStatus = TaskStatus.PENDING
    #hata durmunda kaç kez tekrarladığını tutar
    retry_count:int=0
    #görevin sisteme kayıt edildiği tarih ve saati otomatik kaydeder
    created_at: datetime = field(default_factory=lambda:datetime.now(UTC))
    