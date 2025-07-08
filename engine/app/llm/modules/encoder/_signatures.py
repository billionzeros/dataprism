import dspy
from ._schema import Encoding

class EncoderSignature(dspy.Signature):
    """
    - EncoderSignature is a signature for classifying nodes for a graph database.

    - Given the List of Raw Metrics and their Context, the Model needs to returns a clean, human-friendly name
    and a description for each Metric which is going to be used as a Node in the Knowledge Graph.

    - The Encoding will be used for various purposes, such as data analysis, reporting, or visualization
    in a graph database or data processing pipeline.

    ***IMPORTANT:***
    - The Model needs to return exactly the encodings for each raw metric provided in the input.
    - The Model should not hallucinate any additional metrics that are not provided in the input.
    - The Model should not hallucinate the name of the Metric, it should be the same as the raw metric provided in the input.
    - The Model should not hallucinate the description of the Metric, it should be a concise and clear description of the Metric.
    - The Model should not change the order of the metrics, it should be the same as the raw metrics provided in the input.
    - The Model should not provide any other information, just the name and description of each Metric.
    - The Model should return a list of Encodings for each Metric, where each Encoding contains a clean, human-friendly name and a description for the Metric.
    - The Model should not provide any other information, just the Encodings for each Metric.
    """
    # Input fields
    raw_metrics: list[str] = dspy.InputField(desc="The list of raw metrics to be encoded, such as 'signup_dt' or 'user_age'. This is the name of the node in the graph database.")
    context: str = dspy.InputField(desc="Stringified JSON of the context of all the Metrics to be encoded, such as name, description, and any other relevant attributes. This context provides additional information about each of the metric")
    
    # Output fields
    encoded_metrics: list[Encoding] = dspy.OutputField(
        desc="A List of Encodings for each Metric to be returned",
        T=list[Encoding],
        prefix="encoded_metrics:"
    )