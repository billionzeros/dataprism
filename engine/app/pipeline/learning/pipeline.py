import dspy
import json
import uuid
import mlflow
import logging
from app.utils import APP_LOGGER_NAME
from app.llm.modules.encoder import MetricEncodingModule


logger = logging.getLogger(APP_LOGGER_NAME).getChild("data_ingestion_module")

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
        Initializes the DataIngestion Module.

        Args:
            session_id (uuid.UUID): Unique identifier for the session.
        """
        super().__init__(**kwargs)

        self.session_id = session_id
        """
        Unique identifier for the session.
        This is used to track the ingestion process and associate it with a specific session.
        """

        # LLM Module for encoding Metrics 
        self._encoder = MetricEncodingModule(session_id=self.session_id)
        """
        Encoder Module that will be used to encode the metrics.
        This module will take the input data and encode it into a unique format
        that can be used for further analysis or storage in a knowledge base.
        """

        logger.info(f"DataIngestionModule initialized with session ID: {self.session_id}")

    async def aforward(self, raw_metrics: list[str], context: dict):
        """
        Encodes the provided raw metrics into a structured format using the LLM encoder and LLM Classification
        """

        logger.info(f"Starting Data Ingestion for session ID: {self.session_id}")

        # Validate the input data
        if not isinstance(raw_metrics, list):
            logger.error("Raw metrics should be a list")
            raise ValueError("Raw metrics should be a list")
        
        if not isinstance(context, dict):
            logger.error("Context should be a dictionary")
            raise ValueError("Context should be a dictionary")
        
        with mlflow.start_run(run_name=f"Data Ingestion - {self.session_id}"):
            # Forward the raw metrics and context to the encoder module
            enc_context = json.dumps(context)

            enc_output: dspy.Prediction = await self._encoder.aforward(
                raw_metrics=raw_metrics,
                context=enc_context,
            )

            return dspy.Prediction(
                encodings=enc_output.encodings,
            )

