from src.repositories.base_repository import BaseRepository
from src.clients.database_client import DatabaseClient

class FeedbackRepository(BaseRepository):
    """
    Anonim geri bildirimler (Feedbacks) için veritabanı erişim sınıfı.
    """

    def __init__(self, db_client: DatabaseClient):
        super().__init__(db_client, "feedbacks")
