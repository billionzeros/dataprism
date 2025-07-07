from pydantic import BaseModel
from typing import Any

class CSVHeaderDescriptionContext(BaseModel):
    header_name: str
    """
    Name of the header, e.g. "customer_id", "customer_name", etc.
    """
    
    sample_data: list[Any]
    """
    Sample data for the header, e.g. ["06b8999e2fba1a1fbc88172c00ba8bc7", "4e7b3e00288586ebd08712fdd0374a03"]
    """
