import logging

from google import genai
from sentence_transformers import SentenceTransformer
from app.config.settings import settings
from qdrant_client import QdrantClient

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        logger.info("Initializing Gemini API with google-genai...")
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.gemini_model = settings.GEMINI_MODEL
        logger.info(f"Gemini model '{self.gemini_model}' ready.")

        logger.info(f"Loading embedding model from {settings.MODEL_NAME_OR_PATH}...")
        self.embedding_model = SentenceTransformer(
            settings.MODEL_NAME_OR_PATH, 
            device=settings.DEVICE,
            model_kwargs={
                "torch_dtype": "float16"
            }
        )
        logger.info("Embedding model loaded successfully.")

        logger.info("Initializing Qdrant client...")
        self.qdrant = QdrantClient(url=settings.QDRANT_HOST, timeout=settings.QDRANT_TIMEOUT)
        self.collection_name = settings.QDRANT_COLLECTION
        logger.info("Qdrant client initialized successfully.")


    async def llm_call(self, query: str, system_instruction: str) -> str:
        response = self.client.models.generate_content(
            model=self.gemini_model,
            contents=query,
            config={
                'system_instruction': system_instruction,
                'temperature': 1,
                'max_output_tokens': 6536,
                'top_p': 0.95,
                'response_mime_type': 'application/json',
            }
        )
        return response.text

    async def llm_stream(self, query: str, system_instruction: str):
        response = self.client.models.generate_content_stream(
            model=self.gemini_model,
            contents=query,
            config={
                'system_instruction': system_instruction,
                'temperature': 1,
                'max_output_tokens': 6536,
                'top_p': 0.95,
            }
        )
        for chunk in response:
            if chunk.text:
                yield chunk.text


    async def vector_search(self, query: str, limit: int = 5) -> list[dict]:
        vector = self.embedding_model.encode(query).tolist()
        
        results = self.qdrant.query_points(
            collection_name=self.collection_name,
            query=vector,
            limit=limit,
            with_payload=True,
        )
        return [point.payload for point in results.points]