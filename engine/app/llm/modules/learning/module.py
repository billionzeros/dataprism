import dspy
import json
import uuid
import mlflow
import logging
from app.utils import APP_LOGGER_NAME
from app.llm.modules._schema import MLFlowModel
from ..encoder import MetricEncodingModule


logger = logging.getLogger(APP_LOGGER_NAME).getChild("data_ingestion_module")

class LearningModule(dspy.Module):
    """
    DataIngestion Module is responsible to taking in raw data from various sources and processing them and putting
    them in a strucured format using the Reasoning Capabilities of an LLM onto a Graph Database such as Neo4j

    This Module is responsible for Encoding different type of Metrics to a Specific Encoding Format and then
    Adding an important Data Classification on each Metric, which will be used to build a knowledge base.

    This module is designed to handle the encoding of Metrics ( Data ) from multiple sources,
    including databases, files, and APIs. It processes the data and prepares it
    for further analysis or storage in a knowledge base.
    """

    def __init__(self, session_id: uuid.UUID, tools: list[dspy.Tool], parent_mlflow_model: MLFlowModel | None = None, **kwargs):
        """
        Initializes the DataIngestion Module.

        Args:
            session_id (uuid.UUID): Unique identifier for the session.
            tools (list[dspy.Tool], optional): List of tools to be used in the module.
            parent_mlflow_model (MLFlowModel | None, optional): Parent MLFlow model associated with this module.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(**kwargs)

        self.session_id = session_id
        """
        Unique identifier for the session.
        This is used to track the ingestion process and associate it with a specific session.
        """

        self._parent_mlflow_model = parent_mlflow_model
        """
        Parent MLFlow model associated with this module, this is used to track the lineage of the model
        and associate it with the parent run in MLflow.
        """

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

