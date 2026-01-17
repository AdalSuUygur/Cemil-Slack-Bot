import os
import asyncio
from typing import List, Dict, Any, Optional
from groq import AsyncGroq, RateLimitError, InternalServerError
from src.core.logger import logger
from src.core.exceptions import GroqClientError

class GroqClient:
    """
    Groq Cloud API için dayanıklı (resilient) ASENKRON istemci sınıfı.
    Rate limit durumlarında otomatik olarak yedek modellere geçer.
    """

    # Model hiyerarşisi: İlki ana model, sonrakiler yedek modellerdir.
    MODEL_HIERARCHY = [
        "llama-3.3-70b-versatile",  # Ana Model (Yüksek Zeka)
        "llama-3.1-8b-instant",     # Birinci Yedek (Hızlı/Geniş Limit)
        "mixtral-8x7b-32768"        # İkinci Yedek
    ]

    def __init__(self, api_key: Optional[str] = None, default_model: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            logger.error("[X] GROQ_API_KEY bulunamadı! Lütfen .env dosyasını kontrol edin.")
            raise GroqClientError("Groq API Key eksik.")
        
        try:
            self.client = AsyncGroq(api_key=self.api_key)
            self.default_model = default_model or self.MODEL_HIERARCHY[0]
            logger.info(f"[i] Dayanıklı Groq İstemcisi hazırlandı. Varsayılan Model: {self.default_model}")
        except Exception as e:
            logger.error(f"[X] Groq İstemcisi başlatılırken hata: {e}")
            raise GroqClientError(str(e))

    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = False
    ) -> str:
        """
        Groq üzerinden ASENKRON bir sohbet yanıtı döndürür.
        Rate limit durumunda otomatik olarak hiyerarşideki bir sonraki modele geçer.
        """
        # Kullanıcının istediği modelden başla, yoksa varsayılandan başla
        start_model = model or self.default_model
        
        # Eğer istenen model hiyerarşide varsa oradan başla, yoksa hiyerarşinin başına ekle
        current_hierarchy = self.MODEL_HIERARCHY.copy()
        if start_model not in current_hierarchy:
            current_hierarchy.insert(0, start_model)
        else:
            # İstenen modeli en başa taşı
            current_hierarchy.remove(start_model)
            current_hierarchy.insert(0, start_model)

        last_error = None
        for target_model in current_hierarchy:
            try:
                logger.info(f"[>] Groq sorgusu gönderiliyor ({target_model})...")
                
                completion = await self.client.chat.completions.create(
                    model=target_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=stream
                )
                
                response_text = completion.choices[0].message.content
                logger.info(f"[+] Groq yanıtı alındı ({target_model}).")
                return response_text

            except RateLimitError as e:
                logger.warning(f"[!] Rate Limit aşıldı ({target_model}): {e}")
                logger.info("[i] Yedek modele geçiş yapılıyor...")
                last_error = e
                continue # Bir sonraki modele geç

            except InternalServerError as e:
                logger.warning(f"[!] Groq Sunucu Hatası ({target_model}): {e}")
                logger.info("[i] 2 saniye beklenip tekrar deneniyor...")
                await asyncio.sleep(2)
                last_error = e
                # Sunucu hatasında aynı modeli bir kez daha deneyebiliriz veya devam edebiliriz. 
                # Burada devam etmeyi seçiyoruz.
                continue

            except Exception as e:
                logger.error(f"[X] Groq beklenmedik hata ({target_model}): {e}")
                raise GroqClientError(f"Groq kritik hata: {str(e)}")

        # Eğer tüm modeller denendiyse ve başarısız olduysa
        logger.error("[X] Tüm Groq modelleri denendi ancak yanıt alınamadı.")
        raise GroqClientError(f"Tüm modeller limitlerde veya hatalı. Son hata: {last_error}")

    async def quick_ask(self, system_prompt: str, user_prompt: str, model: Optional[str] = None) -> str:
        """
        Hızlı bir soru-cevap işlemi için ASENKRON kolaylaştırıcı metod.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        return await self.chat_completion(messages, model=model)

    async def close(self):
        """İstemciyi kapatır."""
        await self.client.close()
        logger.info("[i] Groq İstemcisi kapatıldı.")
