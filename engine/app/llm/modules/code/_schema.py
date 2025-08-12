import dspy
class CodeGenerationSignature(dspy.Signature):
    """
    Code Generation Signature is responsible for generating end to end **PYTHON** code snippets based on the
    input prompts. The output should be clean, executable Python code without any markdown formatting.

    The Code Snippet must be clean, executable Python code. 
    Do NOT include:
        - Markdown code block markers (```python or ```)
        - Any explanatory text before or after the code
        - Comments explaining what the code does (unless requested)
    
    DO include:
        - Only valid Python syntax that can be executed directly
        - Proper indentation and formatting
        - Import statements if needed
    
    Example of correct format:
        import math
        result = math.sqrt(16)
        print(result)
    """
    # Input Field
    context: str = dspy.InputField(
        desc="The context is knowledge which the Model need to use in order to product valid code snippets"
    )

    query: str = dspy.InputField(
        desc="The query is the specific question or request for code generation"
    )

    # Output Field
    code: str = dspy.OutputField(
        desc="""
                The Code Snippet must be clean, executable Python code. 
                Do NOT include:
                - Markdown code block markers (```python or ```)
                - Any explanatory text before or after the code
                - Comments explaining what the code does (unless requested)
                
                DO include:
                - Only valid Python syntax that can be executed directly
                - Proper indentation and formatting
                - Import statements if needed
                
                Example of correct format:
                import math
                result = math.sqrt(16)
                print(result)
            """
    )

class CodeValidatorSignature(dspy.Signature):
    """
    Code Validator is Responsible to check and verify that the generated code is upto the standards
    and is free of statistical and known bugs, which needs to revised and worked and fixed again
    """
    # Input Fields
    context: str = dspy.InputField(
        desc="The context in which the code was generated"
    )

    original_query: str = dspy.InputField(
        desc="The original query that was used to generate the code snippet"
    )

    generated_code: str = dspy.InputField(
        desc="The generated code snippet that needs to be validated"
    )

    # Output Fields
    found_issues: list[str] = dspy.OutputField(
        desc="List of found issues in the generated code, which needs to fixed and worked upon again"
    )
    """
    List of found issues in the generated code, which needs to fixed and worked upon again
    """
