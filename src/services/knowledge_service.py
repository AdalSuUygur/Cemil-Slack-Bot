import os
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from src.core.logger import logger
from src.clients import VectorClient, GroqClient

class KnowledgeService:
    """
    Cemil'in 'Bilgi Küpü' (RAG). Dökümanları işler ve soruları yanıtlar.
    Tamamen ücretsiz ve limit-free yapıdadır.
    """

    def __init__(self, vector_client: VectorClient, groq_client: GroqClient):
        self.vector = vector_client
        self.groq = groq_client
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=700,
            chunk_overlap=100
        )

    async def process_knowledge_base(self, folder_path: str = "knowledge_base"):
        """Belirtilen klasördeki dökümanları okur ve indekse ekler."""
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            logger.warning(f"[!] {folder_path} bulunamadı, boş bir tane oluşturuldu.")
            return

        all_texts = []
        all_metadata = []

        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            text = ""
            
            try:
                if filename.endswith(".pdf"):
                    reader = PdfReader(file_path)
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                elif filename.endswith(".txt"):
                    with open(file_path, "r", encoding="utf-8") as f:
                        text = f.read()
                
                if text.strip():
                    chunks = self.splitter.split_text(text)
                    all_texts.extend(chunks)
                    all_metadata.extend([{"source": filename}] * len(chunks))
                    logger.info(f"[+] İşlendi: {filename} ({len(chunks)} parça)")

            except Exception as e:
                logger.error(f"[X] {filename} işlenirken hata: {e}")

        if all_texts:
            self.vector.add_texts(all_texts, all_metadata)
            logger.info(f"[!] {len(all_texts)} parça ile Bilgi Küpü güncellendi.")

    async def ask_question(self, question: str) -> str:
        """Kullanıcının sorusunu dökümanlara göre yanıtlar."""
        try:
            # 1. Benzer metin parçalarını bul
            context_docs = self.vector.search(question, top_k=4)
            
            if not context_docs:
                return "Üzgünüm, bu konuda bilgi küpümde herhangi bir veri bulamadım. 😔"

            # 2. Bağlamı (Context) hazırla
            context_text = "\n\n".join([
                f"--- Kaynak: {doc['metadata'].get('source', 'Bilinmiyor')} ---\n{doc['text']}" 
                for doc in context_docs
            ])

            # 3. LLM'e (Groq) sor
            system_prompt = (
                "Sen Cemil'sin, topluluk asistanısın. Aşağıda sana verilen BAĞLAM (Context) bilgilerini kullanarak "
                "kullanıcının sorusunu yanıtla. Sadece sağlanan bilgileri kullan. Eğer cevap bağlamda yoksa "
                "kibarca bilmediğini söyle. Yanıtların samimi, öz ve ASCII karakterlerle (emojisiz) olsun."
            )
            
            user_prompt = f"BAĞLAM:\n{context_text}\n\nSORU: {question}"
            
            answer = await self.groq.quick_ask(system_prompt, user_prompt)
            return answer

        except Exception as e:
            logger.error(f"[X] KnowledgeService.ask_question hatası: {e}")
            return "Zeka katmanımda bir sorun oluştu, lütfen daha sonra tekrar dene. [X]"
