import dspy
from pydantic import BaseModel
from typing import Literal

classificationType = Literal[
    "point_in_time",
    "pre_aggregated",
]

class Classifications(BaseModel):
    """
    Classification is the association of a raw metric with a specific category or type.

    The Reasoning behind this classification is to help in understanding the nature of the metrics
    and how they can be used for further analysis. This helps in building a knowledge base
    that can be used to derive insights from the metrics.
    The classification can be either "point_in_time" or "pre_aggregated", which
    - "point_in_time" indicates that the metric is a snapshot at a specific moment,
    - "pre_aggregated" indicates that the metric is an aggregation of multiple data points
    over a period of time.

    """
    
    raw_metric: str
    """
    The raw metric that is being classified.
    """

    classification: classificationType
    """
    The classification of the raw metric, which can be either "point_in_time" or "pre_aggregated".
    """



class ClassifierSignature(dspy.Signature):
    """
    ClassifierSignature defines the signature for the Classifier module.

    The Classifier Module is Responsible for taking in raw metrics and the context for the metrics and classifying 
    them into different categories based on the reasoning.

    This helps in understanding the nature of the metrics and how they can be used for further analysis.

    Using these Classification we will build further derived metrics which will be used to build a knowledge base.

    **IMPORTANT**
    - The Classifier Module is not responsible for encoding the metrics, it is only responsible for classifying them.
    - The Classifier Module is responsible for classifying the metrics into different categories based on the reasoning.
    - You have return a list of classification for each of the raw metrics provided.
    - Do not return any other information in the response, only the classification of the metrics.
    - Do not hallucinate or make up any information, only return the classification of the metrics.
    """
    raw_metrics: list[str] = dspy.InputField(
        description="A list of raw metrics to be classified. Each metric should be a string."
    )

    context: str = dspy.InputField(
        description="Properties of the node to be classified, such as name, description, and any other relevant attributes."
    )

    # Output
    classifications: list[Classifications] = dspy.OutputField(
        description="A list of classifications for each raw metric provided."
    )