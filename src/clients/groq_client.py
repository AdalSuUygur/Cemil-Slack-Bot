import os
from typing import List, Dict, Any, Optional
from groq import AsyncGroq
from src.core.logger import logger
from src.core.exceptions import GroqClientError

class GroqClient:
    """
    Groq Cloud API için merkezi ASENKRON istemci sınıfı.
    Yüksek hızlı LLM çıkarımı sağlar ve bot trafik yönetimini asenkron olarak yapar.
    """

    def __init__(self, api_key: Optional[str] = None, default_model: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            logger.error("[X] GROQ_API_KEY bulunamadı! Lütfen .env dosyasını kontrol edin.")
            raise GroqClientError("Groq API Key eksik.")
        
        try:
            # Asenkron istemciyi başlat
            self.client = AsyncGroq(api_key=self.api_key)
            self.default_model = default_model
            logger.info(f"[i] Asenkron Groq İstemcisi hazırlandı. Model: {default_model}")
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
        Groq üzerinden ASENKRON bir sohbet yanıtı (completion) döndürür.
        """
        target_model = model or self.default_model
        try:
            logger.info(f"[>] Asenkron Groq sorgusu gönderiliyor ({target_model})...")
            
            # await ile yanıtı bekle
            completion = await self.client.chat.completions.create(
                model=target_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            
            # Yanıtı al
            response_text = completion.choices[0].message.content
            logger.info("[+] Groq yanıtı asenkron olarak başarıyla alındı.")
            return response_text

        except Exception as e:
            logger.error(f"[X] Groq Chat Completion hatası: {e}")
            raise GroqClientError(f"Groq yanıt üretemedi: {str(e)}")

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
        """
        İstemciyi düzgün bir şekilde kapatır.
        """
        await self.client.close()
        logger.info("[i] Groq İstemcisi kapatıldı.")
