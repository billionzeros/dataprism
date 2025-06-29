from pydantic import BaseModel
from typing import List, Any, Optional

class CSVHeaderDescriptionContext(BaseModel):
    header_name: str
    """
    Name of the header, e.g. "customer_id", "customer_name", etc.
    """
    
    sample_data: List[Any]
    """
    Sample data for the header, e.g. ["06b8999e2fba1a1fbc88172c00ba8bc7", "4e7b3e00288586ebd08712fdd0374a03"]
    """
    
    description: Optional[str] = None
    """
    Description of the header, e.g. "The customer_id is a unique identifier for each customer in the database."
    """