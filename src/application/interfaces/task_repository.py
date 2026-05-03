from abc import abstractmethod, ABC
from src.domain.entities.task import Task
from uuid import UUID
class TaskRepository(ABC):
    """
    Görev (Task) veritabanı işlemleri için standart bir arayüz (interface) tanımlar.
    Bu sınıf doğrudan başlatılamaz; tüm metodlar alt sınıflar tarafından override edilmelidir.
    """
    @abstractmethod
    def save(self,task:Task):
        """
        Yeni bir görev kaydeder.
        :param task: Kaydedilecek olan Task varlığı (entity).
        """
        pass

    @abstractmethod
    def get_by_id(self, task_id:UUID):
        """
        ID üzerinden belirli bir görevi sorgular.
        :param task_id: Sorgulanacak görevin benzersiz UUID'si.
        :return: Bulunan Task nesnesini döner.
        """
        pass
    
    @abstractmethod
    def update(self,task:Task):
        """
        Mevcut bir görevin bilgilerini günceller.
        :param task: Güncel bilgileri içeren Task nesnesi.
        """
        pass

    @abstractmethod
    def delete(self,task_id:UUID):
        """
        Bir görevi sistemden tamamen siler.
        :param task_id: Silinecek görevin benzersiz UUID'si.
        """
        pass
    