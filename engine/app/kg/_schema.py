from dataclasses import dataclass

@dataclass
class KgMetricsNode():
    """
    Represents a Base Node in the Knowledge Graph.
    """

    raw_metric: str
    """
    Raw metrics data associated with the node.
    This field is used to store the raw metrics that are ingested into the Knowledge Graph.
    """

    embedding: list[float]
    """
    Embeddings associated with the node.
    This is the most important field for any Node in the Knowledge Graph.
    It represents the vector embeddings of the node, which are used for similarity search and other operations
    """

    source_id: str
    """
    The upload ID associated with the node.
    This field is used to track the source of the node, such as the file or data source from which the node was created.
    """

    remarks: str | None = None
    """
    Additional remarks or comments about the node,
    Use this field to store any additional information or comments about the node.
    """