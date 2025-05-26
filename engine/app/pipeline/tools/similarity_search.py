import logging
import dspy
from sqlalchemy import select
from app.utils import APP_LOGGER_NAME
from typing import Optional, Sequence
from app.db.models.vector_embedding import VectorEmbedding as EmbeddingModel
from app.db.session import AsyncSessionLocal


logger = logging.getLogger(APP_LOGGER_NAME)

async def similarity_search(query_embedding: list[float], k: int = 5, additional_filters: Optional[dict] = None) -> Sequence[EmbeddingModel]: # query_embedding type hint fixed
    """
    Based on the embedding, find the most simialr embeddings in the Database
    and return the top k most similar embeddings.

    Args:
        - query_embedding: The embedding to search for, must be a list of floats.
        - k: The number of similar embeddings to return.
        - additional_filters: Optional filters to apply to the search.
    """

    logger.info(f"Starting similarity search with query_embedding: {query_embedding}, k: {k}, additional_filters: {additional_filters}")

    # Input validation
    if not query_embedding or not isinstance(query_embedding, list) or not all(isinstance(val, float) for val in query_embedding):
        logger.error("Invalid query_embedding provided. Must be a list of floats.")
        raise ValueError("query_embedding must be a non-empty list of floats.")

    if not isinstance(k, int) or k <= 0:
        logger.error(f"Invalid k value: {k}. Must be a positive integer.")
        raise ValueError("k must be a positive integer.")
    
    async with AsyncSessionLocal() as db:
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
        
        except Exception as e:
            logger.error(f"Error during similarity search database operation: {e}", exc_info=True)
            # Return empty list on error as per original behavior for dspy.Tool
            return []
    
DocumentSimilaritySearchTool = dspy.Tool(
    name="DocumentSimilaritySearch",
    desc="Find the most similar documents based on the provided embedding.",
    func=similarity_search,
    args={
        "query_embedding": dspy.InputField(
            name="query_embedding",
            desc="The embedding to search for, can be a list of floats or a single float for search.",
            type=Sequence[float],
            default=[],
        ),
        "k": dspy.InputField(
            name="k",
            desc="The number of similar embeddings to return.",
            type=int,
            default=5,
            min_value=1
        ),
        "additional_filters": dspy.InputField(
            name="additional_filters",
            desc="Optional filters to apply to the search.",
            type=Optional[dict],
            default=None
        ),
    },
    arg_types={
        "query_embedding": Sequence[float],
        "additional_filters": Optional[dict],
        "k": int,
    },
    arg_desc={
        "query_embedding": "The embedding to search for, can be a list of floats or a single float for search.",
        "k": "The number of similar embeddings to return.",
        "additional_filters": "Optional filters to apply to the search."
    }
)