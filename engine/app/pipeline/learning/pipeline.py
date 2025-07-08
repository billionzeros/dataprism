import dspy
import json
import uuid
import mlflow
import logging
from app.utils import APP_LOGGER_NAME
from app.llm.modules.encoder import MetricEncodingModule, Encoding
from app.llm.embeddings import Embedder
from app.kg import KnowledgeGraph as KG
from app.kg._schema import KgMetricsNode

logger = logging.getLogger(APP_LOGGER_NAME).getChild("learning_pipeline")

class LearningPipeline(dspy.Module):
    """
    LearningPipeline is a module that handles the ingestion of raw metrics data,
    encodes using LLM and then places the encoded data with there embeddings as Metric Nodes in the Knowledge Graph.

    Using the closest Embeddings to each other it starts its Learning Process. 

    Learning Process is a series of steps that involve understanding the data, choosing and creating a plan to analyse the correltion of one encoded metric with another,
    this helps to identify patterns and trends and store these patterns in the Knowledge Graph for future reference using Analysis Nodes.

    This helps the model to remember the pattern it found during the learning process and when it sees any New Event related to the same metric the Knowledge Graph can be queried to find the most relevant patterns and trends.
    and this also helps the model to adjust and make new predictions based on the new data it has seen.
    """

    def __init__(self, session_id: uuid.UUID, **kwargs):
        """
        Initializes the Learning Pipeline.

        Args:
            session_id (uuid.UUID): Unique identifier for the session.
        """
        super().__init__(**kwargs)

        self.session_id = session_id
        """
        Unique identifier for the session.
        """

        self._kg = KG()
        """
        Knowledge Graph instance that will be used to store the encoded metrics.
        The Knowledge Graph is a Semantic Learning Graph that stores the relationships between different metrics and their encoded representations.
        It allows for efficient querying and retrieval of related metrics and their patterns.
        """

        self._embedder = Embedder()
        """
        Embedder instance that will be used to generate embeddings for the encoded metrics.
        The Embedder is responsible for converting the encoded metrics into vector representations that can be used for
        """

        # LLM Module for encoding Metrics 
        self._encoder = MetricEncodingModule(session_id=self.session_id)
        """
        Encoder Module that will be used to encode the metrics.
        This module will take the input data and encode it into a unique format
        that can be used for further analysis or storage in a knowledge base.
        """

        logger.info(f"LearningPipeline initialized with session ID: {self.session_id}")

    async def start(self, raw_metrics: list[str], context: dict):
        """
        Encodes the provided raw metrics into a structured format for the Learning Pipeline.
        """

        logger.info(f"Starting LearningPipeline with session ID: {self.session_id}")

        # Validate the input data
        if not isinstance(raw_metrics, list):
            logger.error("Raw metrics should be a list")
            raise ValueError("Raw metrics should be a list")
        
        if not isinstance(context, dict):
            logger.error("Context should be a dictionary")
            raise ValueError("Context should be a dictionary")
        
        with mlflow.start_run(run_name=f"LearningPipeline_{self.session_id}"):
            # Forward the raw metrics and context to the encoder module
            enc_context = json.dumps(context)

            enc_output: dspy.Prediction = await self._encoder.aforward(
                raw_metrics=raw_metrics,
                context=enc_context,
            )

            logger.info(f"Received Encoded Metrics: {enc_output}")

            if not enc_output or not hasattr(enc_output, 'encodings'):
                logger.error("Encoder did not return valid output")
                raise ValueError("Encoder did not return valid output")
            
            if not isinstance(enc_output.encodings, list):
                logger.error("Encoded metrics should be a list")
                raise ValueError("Encoded metrics should be a list")
            
            encodings = enc_output.encodings

            nodes: list[KgMetricsNode] = []
            
            ems = self._embedder.generate_embeddings([enc.model_dump_json() for enc in encodings if isinstance(enc, Encoding)])
            
            if not ems or not isinstance(ems, list):
                logger.error("Embedder did not return valid embeddings")
                raise ValueError("Embedder did not return valid embeddings")
            
            for i, enc in enumerate(encodings):
                if not isinstance(enc, Encoding):
                    logger.error("Encoded metric is not a valid Encoding")
                    raise ValueError("Encoded metric is not a valid Encoding")
                
                # Create an embedding for each encoding
                
                em = ems[i].values

                if em is None or not isinstance(em, list):
                    logger.error("Embedding values are not valid")
                    raise ValueError("Embedding values are not valid")
                
                nodes.append(KgMetricsNode(
                    raw_metric=enc.raw_metric,
                    embedding=em,
                    source_id=self.session_id.hex,
                    remarks=None
                ))

            self._kg.add_metrics_nodes(nodes)

            logger.info(f"LearningPipeline completed successfully with session ID: {self.session_id}")

