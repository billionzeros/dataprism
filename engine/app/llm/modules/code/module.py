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

        self._generator = dspy.ChainOfThought(
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

        self._max_retries = 5
        """
        Maximum number of retries for code generation.
        """

    def clean_code_output(self, code_string: str) -> str:
        """Remove markdown formatting and extract clean Python code."""
        try:
            # Remove markdown code blocks
            code_string = code_string.strip()
            
            # Handle ```python or ``` at start
            if code_string.startswith('```python'):
                code_string = code_string[9:]
            elif code_string.startswith('```'):
                code_string = code_string[3:]
            
            # Handle ``` at end
            if code_string.endswith('```'):
                code_string = code_string[:-3]
            
            # Remove any leading/trailing whitespace
            code_string = code_string.strip()
            
            return code_string
        except Exception as e:
            raise ValueError(f"Error cleaning code output: {e}")

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
        try:
            retries_left = self._max_retries
            accumulated_issues = []
            enhanced_context = context
            
            while retries_left > 0:
                found_issues: list[str] = []
                
                # Generate code with enhanced context that includes previous issues
                output = await self._generator.aforward(context=enhanced_context, query=query)

                logger.info(f"Generated code snippet for session {self.session_id} (attempt {self._max_retries - retries_left + 1})")

                # Validate the generated code
                validation = await self._validator.aforward(
                    context=enhanced_context,
                    original_query=query,
                    generated_code=output
                )

                if not hasattr(validation, "found_issues"):
                    logger.error(f"Code validation failed for session {self.session_id}")
                    raise ValueError("Code validation failed")
                
                # Collect validation issues
                if hasattr(validation, "found_issues") and len(validation.found_issues) > 0:
                    found_issues.extend(validation.found_issues)

                if not hasattr(output, "code"):
                    logger.error(f"Code generation failed for session {self.session_id}")
                    raise ValueError("Code generation failed")

                if hasattr(output, "code") and output.code:
                    with dspy.PythonInterpreter() as introp:    
                        try:
                            logger.info
                            # execution_code = self.clean_code_output(output.code)
                            # logger.info(f"Executing generated code {execution_code}")
                            # Execute the actual generated code
                            output = introp.execute(output.code)
                            logger.info(f"Code execution successful for session {self.session_id}, {output}")
                        except Exception as e:
                            execution_error = f"Execution error: {str(e)}"
                            found_issues.append(execution_error)
                            logger.warning(f"Code execution failed for session {self.session_id}: {e}")

                if len(found_issues) == 0:
                    logger.info(f"Code generation successful for session {self.session_id}")
                    return dspy.Prediction(
                        code=output.code
                    )
                
                # Add current issues to accumulated issues
                accumulated_issues.extend(found_issues)
                retries_left -= 1
                
                # Enhance context with found issues for next iteration
                if retries_left > 0:
                    issues_context = "\n\nPrevious Generated Code:\n" + "\n".join([f"- {code}" for code in accumulated_issues])
                    enhanced_context = context + issues_context
                    logger.info(f"Retrying code generation for session {self.session_id}. Issues found: {len(found_issues)}. Retries left: {retries_left}")
                else:
                    logger.error(f"Max retries exceeded for session {self.session_id}. Total issues: {len(accumulated_issues)}")

            logger.error(f"Code generation failed after {self._max_retries} attempts for session {self.session_id}")
            raise ValueError(f"Code generation failed after {self._max_retries} attempts. Issues: {'; '.join(accumulated_issues)}")
        
        except Exception as e:
            logger.error(f"Error generating code snippet for session {self.session_id}: {e}")
            raise ValueError("Error generating code snippet")