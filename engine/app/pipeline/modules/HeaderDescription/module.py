import dspy
import logging
import json
from typing import Dict, List
from ._schema import HeaderDescriptionContext
from app.utils import APP_LOGGER_NAME

logger = logging.getLogger(APP_LOGGER_NAME)

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
    headers_description: str = dspy.OutputField(
        desc="Stringfied JSON of each headers and their description",
        format="string",
    )


class PredictHeaderDescription(dspy.Module):
    """
    This Module is responsible for understanding the header of a document which is required for embedding it.
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

    def forward(self, headers_count: int, headers_info: List[HeaderDescriptionContext]):
        """
        Given the headers and sample data, generate a concise description of what the target column header represents
        in the context of this specific file.
        """
        prediction = self._predict_description(
            headers_count=headers_count,
            headers_info=self._encode_ctx_to_str(headers_info),
        )

        if prediction.headers_description:
            try:
                headers_description = self._decode_dict_from_str(prediction.headers_description)
                if not isinstance(headers_description, dict):
                    raise ValueError("Decoded headers_description should be a dictionary")
                
                for header in headers_info:
                    header_name = header.header_name

                    predicted_description = headers_description.get(header_name, "No description available")

                    if isinstance(predicted_description, str):
                        header.description = predicted_description
                    else:
                        logger.warning(f"Predicted description for {header_name} is not a string: {predicted_description}")
                        header.description = "No description available"

            except Exception as e:
                logger.error(f"Error decoding headers_description: {e}")
        else:
            logger.warning("No headers_description found in the prediction")

        return dspy.Prediction(
            headers_info=headers_info,
        )
    
    def _encode_ctx_to_str(self, data: List[HeaderDescriptionContext]):
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