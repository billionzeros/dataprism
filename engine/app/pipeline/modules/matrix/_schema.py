from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Union, Dict, Any

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

class Paragraph(BaseModel):
    """
    Paragraph is a structured text block that can be used to represent a paragraph of text.
    It can be used to represent a paragraph of text in a document, a section of a report, or any other structured text block.
    """
    __type__ = "paragraph"
    
    text: str = Field(
        ...,
        description="The text of the paragraph."
    )

class BulletPoint(BaseModel):
    """
    BulletPoint is a structured text block that can be used to represent a bullet point in a list.
    It can be used to represent a bullet point in a document, a section of a report, or any other structured text block.
    """
    __type__ = "bullet_point"

    text: str = Field(
        ...,
        description="The text of the bullet point."
    )

class BarGraph(BaseModel):
    """
    BarGraph is a structured representation of a bar graph.
    It can be used to represent a bar graph in a document, a section of a report, or any other structured text block.
    """
    __type__ = "bar_graph"

    title: str = Field(
        ...,
        description="The title of the bar graph."
    )

    x_axis_label: str = Field(
        ...,
        description="The label for the x-axis of the bar graph."
    )
    y_axis_label: str = Field(
        ...,
        description="The label for the y-axis of the bar graph."
    )
    x_axis_type: Literal['categorical', 'numerical'] = Field(
        default='categorical',
        description="The type of the x-axis. Can be 'categorical' or 'numerical'. Defaults to 'categorical'."
    )
    y_axis_type: Literal['categorical', 'numerical'] = Field(
        default='numerical',
        description="The type of the y-axis. Can be 'categorical' or 'numerical'. Defaults to 'numerical'."
    )
    color: Optional[str] = Field(
        default=None,
        description="The color of the bars in the bar graph. If not provided, a default color will be used."
    )

class LineGraph(BaseModel):
    """
    LineGraph is a structured representation of a line graph.
    It can be used to represent a line graph in a document, a section of a report, or any other structured text block.
    """
    __type__ = "line_graph"

    title: str = Field(
        ...,
        description="The title of the line graph."
    )
    x_axis_label: str = Field(
        ...,
        description="The label for the x-axis of the line graph."
    )
    y_axis_label: str = Field(
        ...,
        description="The label for the y-axis of the line graph."
    )
    x_axis_type: Literal['categorical', 'numerical'] = Field(
        default='categorical',
        description="The type of the x-axis. Can be 'categorical' or 'numerical'. Defaults to 'categorical'."
    )
    y_axis_type: Literal['categorical', 'numerical'] = Field(
        default='numerical',
        description="The type of the y-axis. Can be 'categorical' or 'numerical'. Defaults to 'numerical'."
    )
    color: Optional[str] = Field(
        default=None,
        description="The color of the line in the line graph. If not provided, a default color will be used."
    )

class Table(BaseModel):
    """
    Table is a structured representation of a table.
    It can be used to represent a table in a document, a section of a report, or any other structured text block.
    """
    __type__ = "table"
    
    title: str = Field(
        ...,
        description="The title of the table."
    )
    headers: List[str] = Field(
        ...,
        description="The headers of the table."
    )
    rows: List[List[str]] = Field(
        ...,
        description="The rows of the table, where each row is a list of strings."
    )

class ErrorMessage(BaseModel):
    """
    ErrorMessage is a structured representation of an error message.
    It can be used to represent an error message in a document, a section of a report, or any other structured text block.
    """
    __type__ = "error_message"
    
    message: str = Field(
        ...,
        description="The error message text."
    )
    code: Optional[int] = Field(
        default=None,
        description="An optional error code associated with the error message."
    )


class FinalResult(BaseModel):
    """
    FinalResult is an List of Different Possible Results such as Paragraph, BulletPoint, BarGraph, LineGraph, or Table.
    It can be used to represent the final result of a query, a section of a report, or any other structured text block.

    Using a List allows formatting the final result in different ways, such as a paragraph, bullet points, bar graph, line graph, or table.
    This allows for flexible representation of the final result, depending on the context and requirements.
    """
    results: List[Union[Paragraph, BulletPoint, BarGraph, LineGraph, Table, ErrorMessage]] = Field(
        ...,
        description="A list of different possible results such as Paragraph, BulletPoint, BarGraph, LineGraph, or Table."
    )