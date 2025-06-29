import logging
from google import genai
from app.settings.config import settings
from app.utils import APP_LOGGER_NAME
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from google.genai.types import EmbedContentConfig
from app.db.models.vector_embedding import VectorEmbedding as EmbeddingModel

logger = logging.getLogger(APP_LOGGER_NAME)

class Embedder:
    """
    Embedder is a class that is responsible for generating embeddings
    for a given text using a specified gemini model.
    """
    def __init__(self, config: Optional[EmbedContentConfig] = None):
        self._embedding_config: Optional[EmbedContentConfig] = None
        self._model = "text-embedding-004"

        if config:
            self._embedding_config = config
    
    def generate_embeddings(self, content: list[str]) :
        """
        Generate embeddings for the given text using the specified gemini model.
        """
        try:
            client = genai.Client(api_key=settings.gemini_api_key)

            response = client.models.embed_content(
                model = self._model,
                contents= content, # type: ignore
                config=self._embedding_config,
            )

            return response.embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return None
        

    async def store_embeddings(self, db: AsyncSession, ems: List[EmbeddingModel]):
        """
        Store the generated embeddings in a database or any other storage.
        """
        if not ems or not isinstance(ems, list):
            raise ValueError("ems must be a non-empty list of EmbeddingModel objects")
        
        db.add_all(ems)
        await db.commit()

        return ems