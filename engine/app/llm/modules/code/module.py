import dspy
import logging
import uuid
from app.utils import APP_LOGGER_NAME
from ._schema import CodeGenerationSignature, CodeValidatorSignature

logger = logging.getLogger(APP_LOGGER_NAME).getChild("code_generation_module")

class CodeGenerationModule(dspy.Module):
    """
    Code Generation Module for generating code snippets based on natural language prompts.
    """

    def __init__(self, session_id: uuid.UUID, **kwargs):
        super().__init__(**kwargs)
        
        self.session_id = session_id
        """
        Unique identifier for the session.
        """

        self._generator = dspy.Predict(
            signature=CodeGenerationSignature,
        )
        """
        Prediction model for generating code snippets.
        """

        self._validator = dspy.ChainOfThought(
            signature=CodeValidatorSignature
        )
        """
        Chain of thought model for validating generated code snippets.
        """

    async def aforward(self, context: str, query: str):
        """
        Generate a code Snippet based on the provided context and query.

        Args:
            context (str): The context in which to generate the code snippet.
            query (str): The specific query or request for code generation.

        Returns:
            str: The generated code snippet.
        Raises:
            ValueError: If the context or query is invalid.
        """
        logger.info(f"Generating code snippet for session {self.session_id}")

        output = await self._generator.aforward(context=context, query=query)

        logger.info(f"Generated code snippet for session {self.session_id}")

        validation = await self._validator.aforward(
            context=context,
            original_query=query,
            generated_code=output
        )

        if not hasattr(validation, "is_valid") or not hasattr(validation, "found_issues"):
            logger.error(f"Code validation failed for session {self.session_id}")
            raise ValueError("Code validation failed")

        return dspy.Prediction(
            code=output.code
        )