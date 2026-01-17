from typing import Optional, Dict, Any
from src.repositories.base_repository import BaseRepository
from src.clients.database_client import DatabaseClient
from src.core.logger import logger
from src.core.exceptions import DatabaseError

class UserRepository(BaseRepository):
    """
    Kullanıcılar tablosuna özel veri erişim sınıfı.
    """

    def __init__(self, db_client: DatabaseClient):
        super().__init__(db_client, "users")

    def get_by_slack_id(self, slack_id: str) -> Optional[Dict[str, Any]]:
        """Slack ID'ye göre kullanıcı getirir."""
        try:
            with self.db_client.get_connection() as conn:
                cursor = conn.cursor()
                sql = f"SELECT * FROM {self.table_name} WHERE slack_id = ?"
                cursor.execute(sql, (slack_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"[X] UserRepository.get_by_slack_id hatası: {e}")
            raise DatabaseError(str(e))

    def update_by_slack_id(self, slack_id: str, data: Dict[str, Any]) -> bool:
        """Slack ID'ye göre kullanıcıyı günceller."""
        set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
        values = list(data.values()) + [slack_id]

        try:
            with self.db_client.get_connection() as conn:
                cursor = conn.cursor()
                sql = f"UPDATE {self.table_name} SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE slack_id = ?"
                cursor.execute(sql, values)
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"[X] UserRepository.update_by_slack_id hatası: {e}")
            raise DatabaseError(str(e))

    def get_users_with_birthday_today(self) -> list:
        """Bugün doğum günü olan kullanıcıları listeler."""
        try:
            with self.db_client.get_connection() as conn:
                cursor = conn.cursor()
                # SQLite'da ay ve gün kontrolü: strftime('%m-%d', birthday)
                sql = f"SELECT * FROM {self.table_name} WHERE strftime('%m-%d', birthday) = strftime('%m-%d', 'now')"
                cursor.execute(sql)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"[X] UserRepository.get_users_with_birthday_today hatası: {e}")

            
    def import_from_csv(self, file_path: str) -> int:
        """
        CSV dosyasından kullanıcıları içe aktarır.
        Özel CSV formatını (Slack ID, First Name, Surname, Birthday, Department) işler.
        Tarih formatını DD.MM.YYYY -> YYYY-MM-DD'ye çevirir.
        Önce mevcut tabloyu temizler.
        """
        import csv
        from datetime import datetime
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            if not rows:
                return 0

            with self.db_client.get_connection() as conn:
                cursor = conn.cursor()
                
                # 1. Tabloyu temizle
                cursor.execute(f"DELETE FROM {self.table_name}")
                
                # 2. Yeni kayıtları ekle
                count = 0
                for row in rows:
                    try:
                        # CSV'den gerekli alanları al ve eşleştir
                        raw_slack_id = row.get('Slack ID', '').strip()
                        # Slack ID bazen "U123 (name)" formatında olabiliyor, sadece ID kısmını al
                        slack_id = raw_slack_id.split(' ')[0] if raw_slack_id else ''
                        
                        first_name = row.get('First Name', '').strip()
                        surname = row.get('Surname', '').strip()
                        
                        # Tam isim oluştur
                        full_name = row.get('Full Name', f"{first_name} {surname}").strip()
                        
                        department = row.get('Department', '').strip()
                        
                        # Tarih formatını düzelt (DD.MM.YYYY -> YYYY-MM-DD)
                        birthday_raw = row.get('Birthday', '').strip()
                        birthday = None
                        if birthday_raw:
                            try:
                                dt = datetime.strptime(birthday_raw, '%d.%m.%Y')
                                birthday = dt.strftime('%Y-%m-%d')
                            except ValueError:
                                # Tarih formatı uymuyorsa None bırak veya logla
                                logger.warning(f"[!] Geçersiz tarih formatı: {birthday_raw} (Satır: {count+2})")
                        
                        if not slack_id:
                            continue

                        sql = f"""
                            INSERT INTO {self.table_name} 
                            (slack_id, first_name, surname, full_name, birthday, department) 
                            VALUES (?, ?, ?, ?, ?, ?)
                        """
                        cursor.execute(sql, (slack_id, first_name, surname, full_name, birthday, department))
                        count += 1
                        
                    except Exception as row_error:
                        logger.warning(f"[!] Satır işlenirken hata (Satır: {count+2}): {row_error}")
                        continue
                
                conn.commit()
                logger.info(f"[+] CSV import tamamlandı. {count} kullanıcı eklendi.")
                return count
                
        except Exception as e:
            logger.error(f"[X] UserRepository.import_from_csv hatası: {e}")
            raise DatabaseError(str(e))
