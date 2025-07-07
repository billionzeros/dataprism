import logging
import dspy
from typing import List

from app.utils import APP_LOGGER_NAME
from app.pipeline.handler.embeddings import Embedder

logger = logging.getLogger(APP_LOGGER_NAME)

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


QueryEmbeddingGeneratorTool = dspy.Tool(
    name="QueryEmbeddingGenerator",
    desc="""
    Generates a vector embedding for a given text query. This is useful when you need to convert text into its vector representation, for example, to then use it with a similarity search tool.

    It returns a list of floats representing the embedding of the query.
    """,
    func=generate_query_embedding,
    arg_types={
        "query": str,
    },
    arg_desc={
        "query": "The text query that needs to be converted into a vector embedding.",
    }
)