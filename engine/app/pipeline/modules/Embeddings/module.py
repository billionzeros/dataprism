import logging
from google import genai
from app.core.config import settings
from app.utils import APP_LOGGER_NAME
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Sequence
from sqlalchemy import select
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
    
    def generate_embeddings(self, content: List[str]) :
        """
        Generate embeddings for the given text using the specified gemini model.
        """
        try:
            client = genai.Client(api_key=settings.gemini_api_key)

            response = client.models.embed_content(
                model = self._model,
                contents= content,
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

    async def similarity_search(self, db: AsyncSession, query_embedding: float, k: int = 5, additional_filters: Optional[dict] = None) -> Sequence[EmbeddingModel]:
        """
        Based on the embedding, find the most simialr embeddings in the Database
        and return the top k most similar embeddings.

        Args:
            - query_embedding: The embedding to search for, can be a list of floats or a single float for search.
            - k: The number of similar embeddings to return.
            - additional_filters: Optional filters to apply to the search.
        """

        if not query_embedding or not isinstance(query_embedding, list) or not all(isinstance(val, float) for val in query_embedding):
            logger.error("Invalid query_embedding provided. Must be a list of floats.")
            raise ValueError("query_embedding must be a non-empty list of floats.")

        if not isinstance(k, int) or k <= 0:
            logger.error(f"Invalid k value: {k}. Must be a positive integer.")
            raise ValueError("k must be a positive integer.")
        
        try:
            stmt = select(EmbeddingModel).where(EmbeddingModel.deleted_at.is_(None))

            if additional_filters:
                for key, value in additional_filters.items():
                    if hasattr(EmbeddingModel, key):
                        stmt = stmt.where(getattr(EmbeddingModel, key) == value)
                    else:
                        logger.warning(f"Invalid filter key: {key}. Skipping this filter.")

            stmt = stmt.order_by(EmbeddingModel.embedding.distance(query_embedding)).limit(k)
            result = await db.execute(stmt)
            similar_embeddings = result.scalars().all()

            return similar_embeddings
        
        except ValueError:
            raise

        except Exception as e:
            logger.error(f"Error during similarity search: {e}")
            return []