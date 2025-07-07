from pydantic import BaseModel


class Encoding(BaseModel):
    """
    LLMEncoding is a structured representation of a node in a knowledge graph.
    This Encoding will be returned by the LLM when it is asked to classify a node for a graph database.
    It contains a clean, human-friendly name and a description for the node, which will be
    """

    raw_metric: str
    """
    The raw metric name that was provided to the LLM for encoding, and for which
    the process of generating is being done.
    """

    clean_name: str
    """
    A clean, human-friendly name for the node, which is used as the identifier in the graph database.
    This name should be concise and descriptive, avoiding any unnecessary complexity or jargon.

    for example, if the raw metric is 'signup_dt', the clean name could be 'Signup Date'.
    """
    
    description: str
    """
    A human-readable description of the node, providing context and details about its purpose and content.
    This description should be concise and clear.
    """

# class Encoding(LLMEncoding):
#     """
#     Encoding is a structured representation of a node in a knowledge graph.
#     This is the Final Encoding that will be used to store the node in the graph database.
#     It extends the LLMEncoding to include additional metadata such as the raw metric name and context.
#     """

#     raw_metric: str
#     """
#     The raw metric name that was provided to the LLM for encoding.
#     This is used to ensure that the clean name and description are consistent with the original metric.
    
#     for example, if the raw metric is 'signup_dt', the raw metric will be 'signup_dt'.
#     """

#     source_identifier: str
#     """
#     Source identifier of the encoding, such as a `upload_id` for CSV,
#     which helps in tracing the origin of the data.
#     This identifier is crucial for linking the encoding back to its source data.
#     """

#     source_type: Literal["CSV", "PDF", "Database"]
#     """
#     Source type of the encoding, such as 'document', 'block', 'csv', etc.
#     This field indicates the type of data source from which the encoding was derived.
#     It helps in categorizing the encoding and understanding its context within the knowledge graph.
#     """


#     def __str__(self):
#         """
#         Returns a string representation of the Encoding object.
#         This is useful for debugging and logging purposes.
#         """
#         return f"Encoding(raw_metric={self.raw_metric}, clean_name={self.clean_name}, description={self.description}, source_identifier={self.source_identifier}, source_type={self.source_type})"
