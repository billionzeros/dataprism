import logging
import dspy
from typing import Dict, List
from pydantic import BaseModel, Field
from sqlalchemy import select
from app.utils import APP_LOGGER_NAME
from typing import Optional
from app.db.session import AsyncSessionLocal
from app.pipeline.handler.embeddings import Embedder
from app.db.models.vector_embedding import VectorEmbedding as EmbeddingModel

logger = logging.getLogger(APP_LOGGER_NAME)

class FindRelevantDocumentResult(BaseModel):
    """
    Represents the result of a document similarity search.
    Contains the ID and embedding of the most similar document.
    """
    id: str
    
    source_type: str
    """
    Source type of the embedding, such as 'document', 'block', 'csv', etc.
    """
    source_identifier: str
    """
    Source identifier of the embedding, such as a `upload_id` for documents,
    """
    related_id: Optional[str] = None
    """
    Related ID of the embedding, if applicable.
    """
    column_or_chunk_name: Optional[str] = None
    """
    Column or chunk name of the embedding, if applicable.
    """
    original_text: Optional[str] = None
    """
    Original text of the embedding, if available.
    """

class SimilaritySearchInput(BaseModel):
    """Input schema for the FindRelevantDocuments tool."""
    query_str: str = Field(
        ..., 
        description="The query string to search for similar embeddings. A detailed query string yields better results."
    )
    k: int = Field(
        default=5, 
        description="The number of similar embeddings to return.",
        ge=1 # ge=1 ensures the value is greater than or equal to 1
    )
    additional_filters: Optional[Dict] = Field(
        default=None, 
        description="Optional dictionary of filters to apply to the search."
    )

async def generate_query_embedding(query: str) -> List[float]:
    """
    Generates a vector embedding for a given text query.

    Args:
        query: The text query to generate an embedding for.

    Returns:
        A list of floats representing the embedding of the query.

    Raises:
        ValueError: If the query is invalid, or if embedding generation fails
                    or returns an unexpected format.
    """
    logger.info(f"Generating embedding for query: '{query}'")
    if not query or not isinstance(query, str):
        logger.error("Invalid query provided. Must be a non-empty string.")
        raise ValueError("Query must be a non-empty string.")

    try:
        embedder = Embedder() 
        
        embeddings_response = embedder.generate_embeddings(content=[query])

        if embeddings_response is None:
            logger.error(f"Embedder failed to generate embeddings for query: '{query}'. Received None.")
            raise ValueError("Failed to generate embedding for the query due to an internal embedder error.")

        if not embeddings_response or len(embeddings_response) == 0:
            logger.error(f"Embedder returned an empty list of embeddings for query: '{query}'.")
            raise ValueError("Failed to generate embedding: embedder returned no embeddings.")

        embedding_object = embeddings_response[0]

        if not hasattr(embedding_object, 'values'):
            logger.error(f"Generated embedding object for query '{query}' does not have 'values' attribute.")
            raise ValueError("Generated embedding object is malformed (missing 'values' attribute).")

        embedding_values = embedding_object.values

        if not isinstance(embedding_values, list) or not all(isinstance(v, (float, int)) for v in embedding_values):
            logger.error(f"Generated embedding values for query '{query}' are not in the expected List[float] format: {embedding_values}")
            raise ValueError("Generated embedding values are not in the expected List[float] format.")
        
        final_embedding = [float(v) for v in embedding_values]

        logger.info(f"Successfully generated embedding for query: '{query}', length: {len(final_embedding)}")
        return final_embedding

    except ValueError:
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred during query embedding generation for '{query}': {e}", exc_info=True)
        raise ValueError(f"An unexpected error occurred while generating embedding: {e}")



async def similarity_search(query_str: str, k: int = 5, additional_filters: Optional[dict] = None) -> List[FindRelevantDocumentResult]:
    """
    Based on the query string, find the most simialr embeddings in the Database
    and return the top k most similar embeddings.

    Args:
        - query_str: The query string to search for similar embeddings, using the most detailed query string results in better results.
        - k: The number of similar embeddings to return.
        - additional_filters: Optional filters to apply to the search.
    """

    logger.info(f"Starting similarity search with query_str: {query_str}, k: {k}, additional_filters: {additional_filters}")

    embedding = await generate_query_embedding(query_str)

    # Input validation
    if not embedding or not isinstance(embedding, list) or not all(isinstance(val, float) for val in embedding):
        logger.error("Invalid embedding provided. Must be a list of floats.")
        raise ValueError("embedding must be a non-empty list of floats.")

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


            stmt = stmt.order_by(EmbeddingModel.embedding.cosine_distance(embedding)).limit(k) 
            
            result = await db.execute(stmt)
            similar_embeddings = result.scalars().all()

            logger.info(f"Found {len(similar_embeddings)} similar embeddings for query_str: '{query_str}'")

            search_result: List[FindRelevantDocumentResult] = [
                FindRelevantDocumentResult(
                    id=str(embedding.id),
                    source_type=embedding.source_type.value,
                    source_identifier=embedding.source_identifier,
                    related_id=embedding.related_id,
                    column_or_chunk_name=embedding.column_or_chunk_name,
                    original_text=embedding.original_text
                ) for embedding in similar_embeddings
            ]

            return search_result
        
        except Exception as e:
            logger.error(f"Error during similarity search database operation: {e}", exc_info=True)
            return []
    
FindRelevantDocuments = dspy.Tool(
    name="FindRelevantDocuments",
    desc=(
        """
            Find the most similar documents based on the provided query string, this TOOL only use is to find relevant documents to the query string, this help gaining more context which might be relevant to the query.

            It return a list of Relevant Documents each containing the following fields:
            - id: The unique identifier of the document, of the table storing different vector_embeddings.
            - source_type: The type of the source, such as 'document', 'block', 'CSV_COLUMN', etc.
            - source_identifier: The identifier of the source, such as an `upload_id` for documents.
            - column_or_chunk_name: The name of the column or chunk, if applicable.
            - related_id: The related ID of the embedding, if applicable.

            source_identfier means different things depending on the source_type:
            - For `CSV_COLUMN` it is the `upload_id` of the CSV file.
            - For `DOCUMENT` it is the `upload_id` of the document.
            - For `BLOCK` it is the `upload_id` of the document or file containing the block.
        """),
    func=similarity_search,
    arg_types={
        "query_str": str,
        "additional_filters": Optional[dict],
        "k": int,
    },
    arg_desc={
        "query_str": "The query string to search for similar embeddings. Using a detailed query string results in better results.",
        "k": "The number of similar embeddings to return.",
        "additional_filters": "Optional filters to apply to the search."
    }
)