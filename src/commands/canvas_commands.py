from typing import List, Optional, Dict, Any
from src.core.logger import logger
from src.core.exceptions import SlackClientError

class CanvasManager:
    """
    Slack Canvas özelliklerini merkezi olarak yöneten sınıf.
    Dökümantasyon: https://api.slack.com/methods?filter=canvases
    """

    def __init__(self, client):
        self.client = client

    def create_canvas(self, title: str, content: Optional[str] = None) -> str:
        """
        Kullanıcı için yeni bir canvas oluşturur.
        """
        try:
            response = self.client.canvases_create(
                title=title,
                content=content
            )
            if response["ok"]:
                canvas_id = response["canvas_id"]
                logger.info(f"[+] Canvas oluşturuldu: {title} (ID: {canvas_id})")
                return canvas_id
            else:
                raise SlackClientError(f"Canvas oluşturulamadı: {response['error']}")
        except Exception as e:
            logger.error(f"[X] canvases.create hatası: {e}", exc_info=True)
            raise SlackClientError(str(e))

    def delete_canvas(self, canvas_id: str) -> bool:
        """
        Belirtilen canvas'ı siler.
        """
        try:
            response = self.client.canvases_delete(canvas_id=canvas_id)
            if response["ok"]:
                logger.info(f"[+] Canvas silindi: {canvas_id}")
                return True
            else:
                raise SlackClientError(f"Canvas silinemedi: {response['error']}")
        except Exception as e:
            logger.error(f"[X] canvases.delete hatası: {e}", exc_info=True)
            raise SlackClientError(str(e))

    def edit_canvas(self, canvas_id: str, changes: List[Dict[str, Any]]) -> bool:
        """
        Mevcut bir canvas'ı günceller.
        'changes' parametresi Slack API formatında [operation, color, content, etc.] olmalıdır.
        """
        try:
            response = self.client.canvases_edit(
                canvas_id=canvas_id,
                changes=changes
            )
            if response["ok"]:
                logger.info(f"[+] Canvas güncellendi: {canvas_id}")
                return True
            else:
                raise SlackClientError(f"Canvas güncellenemedi: {response['error']}")
        except Exception as e:
            logger.error(f"[X] canvases.edit hatası: {e}", exc_info=True)
            raise SlackClientError(str(e))

    def set_access(self, canvas_id: str, access_level: str, user_ids: Optional[List[str]] = None, channel_ids: Optional[List[str]] = None) -> bool:
        """
        Canvas erişim seviyesini ayarlar.
        access_level: 'read' veya 'write' olabilir.
        """
        try:
            response = self.client.canvases_access_set(
                canvas_id=canvas_id,
                access_level=access_level,
                user_ids=user_ids,
                channel_ids=channel_ids
            )
            if response["ok"]:
                logger.info(f"[+] Canvas erişimi ayarlandı: {canvas_id} -> {access_level}")
                return True
            else:
                raise SlackClientError(f"Erişim ayarlanamadı: {response['error']}")
        except Exception as e:
            logger.error(f"[X] canvases.access.set hatası: {e}", exc_info=True)
            raise SlackClientError(str(e))

    def delete_access(self, canvas_id: str, user_ids: Optional[List[str]] = None, channel_ids: Optional[List[str]] = None) -> bool:
        """
        Belirtilen kullanıcılar veya kanallar için canvas erişimini kaldırır.
        """
        try:
            response = self.client.canvases_access_delete(
                canvas_id=canvas_id,
                user_ids=user_ids,
                channel_ids=channel_ids
            )
            if response["ok"]:
                logger.info(f"[+] Canvas erişimi kaldırıldı: {canvas_id}")
                return True
            else:
                raise SlackClientError(f"Erişim kaldırılamadı: {response['error']}")
        except Exception as e:
            logger.error(f"[X] canvases.access.delete hatası: {e}", exc_info=True)
            raise SlackClientError(str(e))

    def lookup_sections(self, canvas_id: str, criteria: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Belirli kriterlere uyan canvas bölümlerini (sections) bulur.
        """
        try:
            response = self.client.canvases_sections_lookup(
                canvas_id=canvas_id,
                criteria=criteria
            )
            if response["ok"]:
                sections = response.get("sections", [])
                logger.info(f"[i] Canvas bölümleri bulundu: {len(sections)} adet (ID: {canvas_id})")
                return sections
            else:
                raise SlackClientError(f"Bölümler sorgulanamadı: {response['error']}")
        except Exception as e:
            logger.error(f"[X] canvases.sections.lookup hatası: {e}", exc_info=True)
            raise SlackClientError(str(e))
