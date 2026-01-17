from typing import List, Optional, Dict, Any
from src.core.logger import logger
from src.core.exceptions import SlackClientError

class PinManager:
    """
    Slack Pin (İğneleme) özelliklerini merkezi olarak yöneten sınıf.
    Dökümantasyon: https://api.slack.com/methods?filter=pins
    """

    def __init__(self, client):
        self.client = client

    def add_pin(self, channel_id: str, timestamp: str) -> bool:
        """
        Bir mesajı kanala iğneler (pin).
        """
        try:
            response = self.client.pins_add(
                channel=channel_id,
                timestamp=timestamp
            )
            if response["ok"]:
                logger.info(f"[+] Mesaj iğnelendi: {timestamp} (Kanal: {channel_id})")
                return True
            else:
                raise SlackClientError(f"Mesaj iğnelenemedi: {response['error']}")
        except Exception as e:
            logger.error(f"[X] pins.add hatası: {e}", exc_info=True)
            raise SlackClientError(str(e))

    def list_pins(self, channel_id: str) -> List[Dict[str, Any]]:
        """
        Bir kanalda iğnelenmiş tüm öğeleri listeler.
        """
        try:
            response = self.client.pins_list(channel=channel_id)
            if response["ok"]:
                items = response.get("items", [])
                logger.info(f"[i] İğnelenmiş öğeler listelendi: {len(items)} adet (Kanal: {channel_id})")
                return items
            else:
                raise SlackClientError(f"İğnelenmiş öğeler alınamadı: {response['error']}")
        except Exception as e:
            logger.error(f"[X] pins.list hatası: {e}", exc_info=True)
            raise SlackClientError(str(e))

    def remove_pin(self, channel_id: str, timestamp: str) -> bool:
        """
        Bir mesajın iğnesini kaldırır (un-pin).
        """
        try:
            response = self.client.pins_remove(
                channel=channel_id,
                timestamp=timestamp
            )
            if response["ok"]:
                logger.info(f"[-] Mesaj iğnesi kaldırıldı: {timestamp} (Kanal: {channel_id})")
                return True
            else:
                raise SlackClientError(f"İğne kaldırılamadı: {response['error']}")
        except Exception as e:
            logger.error(f"[X] pins.remove hatası: {e}", exc_info=True)
            raise SlackClientError(str(e))
