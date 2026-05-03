
class TaskNotFoundError(Exception):
    def __init__(self, task_id):
        super().__init__(f"Task bulunamadı: {task_id}")

class InvalidStatusTransition(Exception):
    def __init__(self, from_status,to_status):
        super().__init__(f"statüs geçersiz:{from_status}->{to_status}")

class UserNotFoundError(Exception):
    def __init__(self, user_id):
        super().__init__(f"user bulunmadı:{user_id}")