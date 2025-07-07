import dspy
import uuid
import logging
import mlflow
from app.utils.logging_config import APP_LOGGER_NAME
from ._signatures import ClassifierSignature, Classifications, classificationType


logger = logging.getLogger(APP_LOGGER_NAME).getChild("metric_classifier_module")

class MetricClassifierModule(dspy.Module):
    """
    MetricClassifier Module is responsible for classifying metrics based on their content.

    This Module will be used to classify different Raw Metrics into Different Derived Metrics
    which will be used to build a knowledge base, Derived Metrics are much more powerful
    to understand and analyse the Raw Metrics.
    """

    def __init__(self, session_id: uuid.UUID, **kwargs):
        """
        Initializes the MetricClassifier Module.

        Args:
            session_id (str): Unique identifier for the session.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(**kwargs)

        self.session_id = session_id
        """
        Unique identifier for the session.
        This is used to track the classification process and associate it with a specific session.
        """

        self._classifier = dspy.ChainOfThought(ClassifierSignature)
        """
        Classifier Module that will be used to classify the metrics.
        This module will take the input data and classify it into different categories based on the reasoning.
        The classification can be either "point_in_time" or "pre_aggregated".
        """

        logger.info(f"MetricClassifier initialized with session ID: {self.session_id}")

    @mlflow.trace(name="Metric Classification Module")
    async def aforward(self, raw_metrics: list[str], context: str):
        """
        Classified the Provided Raw Metrics two type "Point In Time" and "Pre Aggregated" Metrics.

        This helps in understanding the nature of the metrics and how they can be used for further analysis.        
        """

        logger.info(f"Classifying raw metrics: {raw_metrics} with context: {context}")

        if not isinstance(raw_metrics, list):
            logger.error("raw_metrics must be a list of strings")
            raise ValueError("raw_metrics must be a list of strings")
        
        if not isinstance(context, str):
            logger.error("context must be a string")
            raise ValueError("context must be a string")
        
        prediction = await self._classifier.aforward(
            raw_metrics=raw_metrics,
            context=context,
        )

        self._validate_response(raw_metrics, prediction)

        logger.info(f"Classified metrics: {prediction.classifications}")

        return dspy.Prediction(
            classifications=prediction.classifications,
        )

    def _validate_response(self, raw_metrics: list[str], response: dspy.Prediction):
        """
        Validates the response from the classifier module.

        Args:
            raw_metrics (list[str]): List of raw metrics that were classified.
            response (dspy.Prediction): The response from the classifier module.

        Raises:
            ValueError: If the response does not match the expected format.
        """
        if not isinstance(response, dspy.Prediction):
            raise ValueError("Response must be a dspy.Prediction object")
        
        if not hasattr(response, 'classifications'):
            raise ValueError("Response must contain 'classifications' attribute")
        
        if not isinstance(response.classifications, list):
            raise ValueError("'classifications' attribute must be a list")

        if len(response.classifications) != len(raw_metrics):
            raise ValueError("The number of classifications must match the number of raw metrics")
        
        validate_metrics = set(raw_metrics)

        valid_classifications: list[classificationType] = ["point_in_time", "pre_aggregated"]

        for classification in response.classifications:
            if not isinstance(classification, Classifications):
                raise ValueError("Each classification must be an instance of Classifications")
            
            if not hasattr(classification, 'raw_metric'):
                raise ValueError("Classification must have 'raw_metric' attribute")
            
            if not hasattr(classification, 'classification'):
                raise ValueError("Classification must have 'classification' attribute")
            
            if classification.raw_metric not in validate_metrics:
                raise ValueError(f"Raw metric '{classification.raw_metric}' not found in the provided raw metrics")
            
            if classification.classification not in valid_classifications:
                raise ValueError(f"Classification '{classification.classification}' is not valid. Must be one of {valid_classifications}")

            validate_metrics.remove(classification.raw_metric)
