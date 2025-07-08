import dspy
import logging
import json
import mlflow
from typing import Dict, List
from pydantic import BaseModel, Field
from ._schema import CSVHeaderDescriptionContext
from app.utils import APP_LOGGER_NAME

logger = logging.getLogger(APP_LOGGER_NAME)

class HeaderDescriptions(BaseModel):
    """
    Represents the description of a header in a CSV file.
    This Schema is will be used to return the description of a header
    in the CSV file, in a concise and clear manner.
    """
    header_name: str = Field(
        ...,
        description="The name of the header in the CSV file, e.g. 'customer_id', 'customer_name', etc."
    )
    """
    Name of the header, e.g. "customer_id", "customer_name", etc, do not change or hallucinate the name of the header
    """

    description: str
    """
    Description of the header, e.g. "The customer_id is a unique identifier for each customer in the database."
    """

class GenerateHeaderDescription(dspy.Signature):
    """
    Given the headers and sample data, generate a concise description of what the target column header represents
    in the context of this specific file.

    Important:
	- Return the Description for Each Header as the HeadersCount Provided in the Context.
	- Dont change the order and the name of the headers. [Very Important]
	- Do not provide any other information, just the description of each header. [Very Important]
	- Provide the Description of each header in the CSV file, in a concise and clear manner, 
	- Maximum 50 words, Default: "No description available".
	- If unable to provide the description, please mention "No description available".
	- Make sure to provide the description in a single line, without any new lines or bullet points, try to be as concise as possible.

    """
    # Input Fields
    headers_count: int = dspy.InputField(
        desc="The number of headers in the CSV file, you should generate the description for each header.",
        format="int",
    )

    headers_info: str = dspy.InputField(
        desc="Stringfied JSON of the headers and comma seperated sample data",
        format="string",
    )

    # Output Fields
    descriptions: list[HeaderDescriptions] = dspy.OutputField(
        desc="A list of descriptions for each header in the CSV file, each description should be concise and clear.",
        T=List[HeaderDescriptions],
        prefix="descriptions:",
    )


class ProcessCSV(dspy.Module):
    """
    This Module is responsible for understanding the CSV - Which is understanding each of the headers the CSV Store - which is then required for embedding it with some additional context.
    
    Based on the json provided of the format:
    sample_data = [
    {
        "header": "customer_id",
        "sample_data": ["06b8999e2fba1a1fbc88172c00ba8bc7", "4e7b3e00288586ebd08712fdd0374a03"]
    },
    {
        "header": "customer_name",
        "sample_data": ["John Doe", "Jane Smith"]
    },
    ]

    The Module will send the data to understand the context of the header and then build a embedding context for
    each header

    The context used for embedding will look like:
    context = {
        "header": "customer_id",
        "sample_data": ["06b8999e2fba1a1fbc88172c00ba8bc7", "4e7b3e00288586ebd08712fdd0374a03"],
        "context": "The customer_id is a unique identifier for each customer in the database. It is used to track customer information and transactions."
    }

    After the context is built, the module will send the data to the embedding service to build the embedding for each header
    The embedding will be stored in the database for further use.
    """

    def __init__(self):
        self._predict_description = dspy.Predict(GenerateHeaderDescription)

    async def aforward(self, headers_count: int, headers_info: List[CSVHeaderDescriptionContext]):
        """
        Given the headers and sample data, generate a concise description of what the target column header represents
        in the context of this specific file.
        """

        try:
            logger.info("Starting Header Description Prediction")

            with mlflow.start_run():
                prediction = await self._predict_description.aforward(
                    headers_count=headers_count,
                    headers_info=self._encode_ctx_to_str(headers_info),
                )

                if not prediction.descriptions:
                    logger.warning("No header descriptions found in the prediction")
                    raise ValueError("No header descriptions found in the prediction")
                
                if not isinstance(prediction.descriptions, list):
                    logger.error("Header descriptions should be a list")
                    raise ValueError("Header descriptions should be a list")
                
                if len(prediction.descriptions) != headers_count:
                    logger.error(f"Expected {headers_count} header descriptions, but got {len(prediction.descriptions)}")
                    raise ValueError(f"Expected {headers_count} header descriptions, but got {len(prediction.descriptions)}")
                
                descriptions: dict[str, HeaderDescriptions] = {}
                for header_desc in prediction.descriptions:
                    if not isinstance(header_desc, HeaderDescriptions):
                        logger.error(f"Header description should be a dictionary, got {type(header_desc)}")
                        raise ValueError("Header description should be a dictionary")
                                        
                    header_name = header_desc.header_name
                    description = header_desc.description

                    if not header_name or not isinstance(header_name, str):
                        logger.error(f"Invalid header name: {header_name}")
                        raise ValueError("Invalid header name in the prediction")
                    
                    if not description or not isinstance(description, str):
                        logger.error(f"Invalid description for header {header_name}: {description}")
                        raise ValueError(f"Invalid description for header {header_name}")
                    
                    descriptions[header_name] = HeaderDescriptions(
                        header_name=header_name,
                        description=description
                    )
                    
                        
                for header in headers_info:
                    header_name = header.header_name

                    prediction = descriptions.get(header_name, "No description available")

                    if isinstance(prediction, HeaderDescriptions):
                        header.description = prediction.description
                    else:
                        logger.warning(f"Predicted description for {header_name} not returned by the model, using default value")
                        header.description = "No description available"

                return dspy.Prediction(
                    headers_info=headers_info,
                )
        except Exception as e:
            logger.error(f"Error in ProcessCSV Module: {e}")
            raise e
            
    def _encode_ctx_to_str(self, data: List[CSVHeaderDescriptionContext]):
        """
        Encode the type List[HeaderDescriptionContext] into a string format.
        This is used to send the headers_info to the LLM model for processing
        """
        try:
            encoded_headers = json.dumps([header.model_dump_json() for header in data], indent=4)

            if not isinstance(encoded_headers, str):
                raise ValueError("Encoded headers should be a string")
            
            return encoded_headers
        except Exception as e:
            logger.error(f"Error parsing headers_info: {e}")
            raise
    
    def _encode_dict_to_str(self, data: Dict[str, str]):
        """
        Encode the headers_info dictionary into a string format.
        This is used to send the headers_info to the LLM model for processing
        """
        try:
            encoded_headers = json.dumps(data, indent=4)

            if not isinstance(encoded_headers, str):
                raise ValueError("Encoded headers should be a string")
            
            return encoded_headers
        except Exception as e:
            logger.error(f"Error parsing headers_info: {e}")
            raise

    def _decode_dict_from_str(self, data: str):
        """
        Decode the data string into a dictionary format.
        This is used to parse the response from the LLM model
        """
        try:
            decoded_headers = json.loads(data)
            if not isinstance(decoded_headers, dict):
                raise ValueError("Decoded headers should be a dictionary")
            
            return decoded_headers
        except Exception as e:
            logger.error(f"Error parsing headers_info: {e}")
            raise