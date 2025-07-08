from pydantic import BaseModel
from typing import Any

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

class CSVContext(BaseModel):
    """
    Context needed for Encoding CSV Information.
    This context is used to provide additional information about the CSV headers and their sample data.
    """
    
    header_name: str
    """
    Name of the header, e.g. "customer_id", "customer_name", etc.
    """
    
    sample_data: list[Any]
    """
    Sample data for the header, e.g. ["06b8999e2fba1a1fbc88172c00ba8bc7", "4e7b3e00288586ebd08712fdd0374a03"]
    """