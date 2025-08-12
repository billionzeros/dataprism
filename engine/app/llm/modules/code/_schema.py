import dspy
class CodeGenerationSignature(dspy.Signature):
    """
    Code Generation Signature is reponsible for generating end to end **PYTHON** code snippets based on the
    input prompts
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
        desc="The code is the generated code snippet that corresponds to the query"
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
    is_valid: bool = dspy.OutputField(
        desc="Indicates whether the generated code is valid or not"
    )
    """
    Indicates whether the generated code is valid or not.
    """

    found_issues: list[str] = dspy.OutputField(
        desc="List of found issues in the generated code, which needs to fixed and worked upon again"
    )
    """
    List of found issues in the generated code, which needs to fixed and worked upon again
    """
