import dspy
from typing import Literal

NodeType = Literal[
    "Metric",       # A 'Metric' is a quantitative, numerical value that can be measured or tracked over time (e.g., sales, temperature, user count, etc).
    "Dimension"     # A 'Dimension' is a categorical attribute used to slice, filter, or describe data (e.g., country, product category, plan type, etc).
    "Event"         # An 'Event' describes something that happened at a point in time (e.g., campaign name, feature release, etc).
    "Identifier"    # An 'Identifier' is a unique key used to identify a specific entity (e.g., user_id, order_id, session_id, etc).
    "Unknown",     # Use 'Unknown' for columns that don't fit, like free-text notes or irrelevant data.
]


class EncoderSignature(dspy.Signature):
    """
    EncoderSignature is a signature for classifying nodes for a graph database.
    The classification will be used for various purposes, such as data analysis, reporting, or visualization
    in a graph database or data processing pipeline.
    The classification helps in understanding the role of each node in the graph and how it relates to
    other nodes, enabling better data management and insights extraction.

    The classification is based on the following types:
    - A 'Metric' is a quantitative, numerical value that can be measured or tracked over time (e.g., sales, temperature, user count).
    - A 'Dimension' is a categorical attribute used to slice, filter, or describe data (e.g., country, product category, plan type).
    - An 'Event' describes something that happened at a point in time (e.g., campaign name, feature release).
    - An 'Identifier' is a unique key used to identify a specific entity (e.g., user_id, order_id, session_id).
    - Use 'Unknown' for columns that don't fit, like free-text notes or irrelevant data.
    """
    # Input fields
    node_properties: dict = dspy.InputField(desc="Properties of the node to be classified, such as name, description, and any other relevant attributes.")
    
    # Output fields
    node_type: NodeType = dspy.OutputField(desc="The type of the node in the graph, classified as one of the predefined types: Metric, Dimension, Event, Identifier, or Unknown.")

    clean_name: str = dspy.OutputField(desc="A clean, human-friendly name for the header. E.g., 'signup_dt' becomes 'Signup Date'.")

    description: str = dspy.OutputField(desc="A concise, one-sentence description of what this data represents.")