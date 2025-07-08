from pydantic import BaseModel, Field
from typing import Optional, Union, Dict, Any

class DirectAnswerActionPlan(BaseModel):
    """
    Direct Answer Action Plan defines a single action to be taken within a larger plan.
    It is to be used when the system can directly answer the user's query without needing to call any tools.
    E.g.
    - {"answer_text": "The user's query is ambiguous. Please provide more specific details."}
    - {"answer_text": "The weather in London is sunny with a high of 25 degrees Celsius."}
    - {"answer_text": "The sum of 5 and 10 is 15."}
    - {"answer_text": "The user's query is not clear. Please provide more details."}
    """
    answer_text: Optional[str] = Field(
        default=None,
        description="If action_type is 'answer_directly', this field contains the text of the summary or direct answer to be provided to the user or for internal use."
    )

class ToolActionPlan(BaseModel):
    """
    Tool Action Plan defines a single action to be taken within a larger plan.
    It is to be used when the system needs to call a tool to gather information or perform an action.
    
    It includes the name of the tool to be called and the input parameters for that tool.
    - The tool_args can be a dictionary of parameters or a single string argument.
    - The tool_name should match the name of a registered tool in the system.
    - The tool_args should be structured according to the tool's expected input format.
    - This allows for flexible tool calls, including those that require complex inputs or multiple parameters.
    - The tool_args can be a dictionary of parameters or a single string argument.

    E.g.
    - {"tool_name": "get_weather", "tool_args": {"city": "London"}}
    - {"tool_name": "database_query", "tool_args": {query: "SELECT name FROM users WHERE id = 10;"}}
    """
    tool_name: str = Field(
        description="If action_type is 'call_tool', this is the name of the tool to be invoked (e.g., 'SearchEmbedding', get_weather', 'calculator', )."
    )

    tool_args: Optional[Union[Dict[str, Any], str]] = Field(
        default=None,
        description="If action_type is 'call_tool', this is the input for the tool. It can be a dictionary of parameters (e.g., {'query': '...', 'limit': 10}) or a single string argument."
    )

class ToolExecutionResult(BaseModel):
    """
    ToolExecutionResult is a structured representation of the result of a tool call.
    It can be used to represent the result of a tool call in a document, a section of a report, or any other structured text block.
    """
    tool_name: str = Field(
        ...,
        description="The name of the tool that was called."
    )
    tool_args: Optional[Union[Dict[str, Any], str]] = Field(
        default=None,
        description="The input arguments that were passed to the tool."
    )
    result: Any = Field(
        ...,
        description="The result of the tool call. This can be any type of data, depending on the tool's output."
    )
    error: Optional[str] = Field(
        default=None,
        description="An optional error message if the tool call failed."
    )