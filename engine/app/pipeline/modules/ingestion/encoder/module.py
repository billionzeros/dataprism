import logging
import uuid 
import mlflow
import dspy
from app.utils import APP_LOGGER_NAME
from ._signatures import EncoderSignature
from ._schema import Encoding
from app.pipeline.modules._schema import MLFlowModel

logger = logging.getLogger(APP_LOGGER_NAME).getChild("data_ingestion_module")


class MetricEncodingModule(dspy.Module):
    """
    This Module is responsible for Encoding different type of Metrics to a unique Encoding Format
    using the Reasoning Capabilities on an LLM, build them into a knowledge base.
    
    This module is designed to handle the encoding of Metrics ( Data ) from multiple sources,
    including databases, files, and APIs. It processes the data and prepares it
    for further analysis or storage in a knowledge base.

    Returns:
        dspy.Prediction: A prediction containing the encoded metrics, containing 'encoded_metrics' attribute,
        which is a list of Encodings for each Metric
    """

    def __init__(self, session_id: uuid.UUID, **kwargs):
        """
        Initializes the MetricEncoding Module.

        Args:
            session_id (uuid.UUID): Unique identifier for the session.
            tools (list[dspy.Tool], optional): List of tools to be used in the module.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(**kwargs)

        self.session_id = session_id
        """
        Unique identifier for the session.
        This is used to track the ingestion process and associate it with a specific session.
        """

        self._encoder = dspy.Predict(
            signature=EncoderSignature, config=dict(
                max_output_tokens=1000,
            )
        )
        """
        The encoder predict function that will be used to encode the metrics.
        using the reasoning capabilities of the LLM.
        This function will take the input data and encode it into a unique format
        that can be used for further analysis or storage in a knowledge base.
        """

        logger.info(f"MetricEncodingModule initialized with session ID: {self.session_id}")

    @mlflow.trace(name="Metric Encoding Module")
    async def aforward(self, raw_metrics: list[str], context: str,):
        """
        Encodes the provided raw metrics into a structured format using the LLM encoder.

        Args:
            raw_metrics (list[str]): A list of raw metrics to be encoded. Each metric should be a string.
            context (dict): Properties of the node to be classified, such as name, description, and any other relevant attributes.

        Returns:
            dspy.Prediction: A prediction containing the encoded metrics, which includes a clean, human-friendly name and a description for each metric.
        Raises:
            ValueError: If the response from the encoder does not meet the expected criteria.
        """
        logger.info(f"Encoding Metrics: {raw_metrics}")

        prediction = await self._encoder.aforward(raw_metrics=raw_metrics, context=context)
        
        # Validate the response to ensure it contains the expected structure and data types
        self._validate_response(raw_metrics, prediction)

        logger.info(f"Encoded Metrics: {prediction.encoded_metrics}")

        return dspy.Prediction(
            encodings=prediction.encoded_metrics,
        )
        
    def _validate_response(self, raw_metrics: list[str], response: dspy.Prediction):
        """
        Validates and Parses the Response from the LLM Encoder to a structured format.
        Args:
            raw_metrics (list[str]): The list of raw metrics that were provided to the LLM for encoding.
            response (dspy.Prediction): The response from the LLM containing encoded metrics.

        Returns:
            list[Encoding]: A list of Encodings for each Metric.

        Raises:
            ValueError: If the response does not contain the expected structure or data types.
        """        
        if not response:
            logger.error("No Encoded Metrics found in the response")
            raise ValueError("No Encoded Metrics found in the response")
    
        if not hasattr(response, 'encoded_metrics'):
            logger.error("Response does not contain 'encoded_metrics' attribute")
            raise ValueError("Response does not contain 'encoded_metrics' attribute")

        if not isinstance(response.encoded_metrics, list):
            logger.error("Encoded Metrics should be a list")
            raise ValueError("Encoded Metrics should be a list")

        encoded_metrics: list[Encoding] = response.encoded_metrics

        if len(encoded_metrics) != len(raw_metrics):
            logger.error(f"Encoded Metrics length {len(encoded_metrics)} does not match the raw metrics length {len(raw_metrics)}")
            raise ValueError(f"Encoded Metrics length {len(encoded_metrics)} does not match the raw metrics length {len(raw_metrics)}")
        
        validate_metrics = set(raw_metrics)

        for encoded_metric in encoded_metrics:
            if not isinstance(encoded_metric, Encoding):
                logger.error(f"Encoded Metric should be an instance of Encoding, got {type(encoded_metric)}")
                raise ValueError("Encoded Metric should be an instance of Encoding")

            if not hasattr(encoded_metric, 'raw_metric'):
                logger.error("Encoded Metric does not have 'raw_metric' attribute")
                raise ValueError("Encoded Metric does not have 'raw_metric' attribute")
            
            if not hasattr(encoded_metric, 'clean_name'):
                logger.error("Encoded Metric does not have 'clean_name' attribute")
                raise ValueError("Encoded Metric does not have 'clean_name' attribute")
            
            if not hasattr(encoded_metric, 'description'):
                logger.error("Encoded Metric does not have 'description' attribute")
                raise ValueError("Encoded Metric does not have 'description' attribute")
            
            if encoded_metric.raw_metric not in validate_metrics:
                logger.error(f"Encoded Metric raw_metric '{encoded_metric.raw_metric}' does not match any of the provided raw metrics")
                raise ValueError(f"Encoded Metric raw_metric '{encoded_metric.raw_metric}' does not match any of the provided raw metrics")
            
            validate_metrics.remove(encoded_metric.raw_metric)