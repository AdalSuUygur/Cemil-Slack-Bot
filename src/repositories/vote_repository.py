from src.core.logger import logger
from src.core.exceptions import DatabaseError
from src.repositories.base_repository import BaseRepository
from src.clients.database_client import DatabaseClient

class VoteRepository(BaseRepository):
    """
    Kullanıcı oyları (Votes) için veritabanı erişim sınıfı.
    """

    def __init__(self, db_client: DatabaseClient):
        super().__init__(db_client, "votes")

    def has_user_voted(self, poll_id: str, user_id: str, option_index: int = None) -> bool:
        """
        Kullanıcının belirli bir oylamada (veya belirli bir seçenekte) oy verip vermediğini kontrol eder.
        """
        query = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE poll_id = ? AND user_id = ?"
        params = [poll_id, user_id]
        
        if option_index is not None:
            query += " AND option_index = ?"
            params.append(option_index)
            
        try:
            with self.db_client.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                row = cursor.fetchone()
                return row["count"] > 0 if row else False
        except Exception as e:
            logger.error(f"[X] VoteRepository.has_user_voted hatası: {e}")
            raise DatabaseError(str(e))

    def delete_vote(self, poll_id: str, user_id: str, option_index: int) -> bool:
        """Belirli bir oyu siler (Oy Geri Alma)."""
        try:
            with self.db_client.get_connection() as conn:
                cursor = conn.cursor()
                sql = f"DELETE FROM {self.table_name} WHERE poll_id = ? AND user_id = ? AND option_index = ?"
                cursor.execute(sql, (poll_id, user_id, option_index))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"[X] VoteRepository.delete_vote hatası: {e}")
            raise DatabaseError(str(e))

    def delete_all_user_votes(self, poll_id: str, user_id: str) -> bool:
        """Kullanıcının oylamadaki TÜM oylarını siler (Tekli seçim için temizlik)."""
        try:
            with self.db_client.get_connection() as conn:
                cursor = conn.cursor()
                sql = f"DELETE FROM {self.table_name} WHERE poll_id = ? AND user_id = ?"
                cursor.execute(sql, (poll_id, user_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"[X] VoteRepository.delete_all_user_votes hatası: {e}")
            raise DatabaseError(str(e))
