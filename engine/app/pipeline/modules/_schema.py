from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Union

class GenerativeModel(str, Enum):
    """
    An enumeration for Large Language Model identifiers.
    """
    GEMINI_2_0_FLASH = "gemini/gemini-2.0-flash"
    GEMINI_1_5_PRO = "gemini/gemini-1.5-pro-latest"
    GEMINI_1_0_PRO = "gemini/gemini-1.0-pro"

    def __str__(self):
        """Ensures the string representation is the model's value."""
        return self.value
    

# Result Class
# This class is used to represent the final result of a query, which can be a paragraph, bullet point, bar graph, line graph, table, or error message.

class Paragraph(BaseModel):
    """
    Paragraph is a structured text block that can be used to represent a paragraph of text.
    It can be used to represent a paragraph of text in a document, a section of a report, or any other structured text block.
    """
    type: Literal['paragraph'] = "paragraph"
    """
    The type of the structured text block. This is used to identify the type of the structured text block.
    It is used to represent a paragraph of text in a document, a section of a report, or any other structured text block.
    """
    
    text: str = Field(
        ...,
        description="The text of the paragraph."
    )
    """
    The text of the paragraph. This is the main content of the paragraph and can be any string.
    """

class BulletPoint(BaseModel):
    """
    BulletPoint is a structured text block that can be used to represent a bullet point in a list.
    It can be used to represent a bullet point in a document, a section of a report, or any other structured text block.
    """
    type: Literal['bullet_point'] = "bullet_point"

    text: str = Field(
        ...,
        description="The text of the bullet point."
    )

class BarGraph(BaseModel):
    """
    BarGraph is a structured representation of a bar graph.
    It can be used to represent a bar graph in a document, a section of a report, or any other structured text block.
    """


    type: Literal['bar_graph'] = "bar_graph"
    """
    The type of the structured text block. This is used to identify the type of the structured text block.
    It is used to represent a paragraph of text in a document, a section of a report, or any other structured text block.
    """

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

    type: Literal['line_graph'] = "line_graph"
    """
    The type of the structured text block. This is used to identify the type of the structured text block.
    It is used to represent a line graph in a document, a section of a report, or any other structured text block.
    """

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


    type: Literal['table'] = "table"
    """
    The type of the structured text block. This is used to identify the type of the structured text block.
    It is used to represent a table in a document, a section of a report, or any other structured text block.
    """
    
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

    type: Literal['error_message'] = "error_message"
    """
    The type of the structured text block. This is used to identify the type of the structured text block.
    It is used to represent an error message in a document, a section of a report, or any other structured text block.
    """
    
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