import dspy
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
    tool_name: Optional[str] = Field(
        default=None,
        description="If action_type is 'call_tool', this is the name of the tool to be invoked (e.g., 'SearchEmbedding', get_weather', 'calculator', )."
    )

    tool_args: Optional[Union[Dict[str, Any], str]] = Field(
        default=None,
        description="If action_type is 'call_tool', this is the input for the tool. It can be a dictionary of parameters (e.g., {'query': '...', 'limit': 10}) or a single string argument."
    )


class PlanQuerySignature(dspy.Signature):
    """
    Given the user query, chat history, available tools, and optional feedback from a previous attempt,
    understand the query, create a step-by-step plan, and identify tool calls.
    Plan actions: 'call_tool(<tool_name>, <tool_input>)' or 'answer_directly(<summary>)'.
    """
    # Input fields
    user_query: str = dspy.InputField(desc="The user's current question or statement.")
    chat_history = dspy.InputField(desc="The history of the conversation.", T=dspy.History)
    available_tools_desc = dspy.InputField(desc="Description of available tools.")
    feedback_on_previous_attempt = dspy.InputField(desc="Optional feedback from a previous execution cycle for this query.")
    
    # Output fields
    thought_plan: str = dspy.OutputField(desc="Step-by-step thinking process for the plan.", prefix="plan_thought:")
    plan: List[DirectAnswerActionPlan | ToolActionPlan] = dspy.OutputField(desc="List of structured actions to execute as per the defined format, This should be a valid JSON list of ActionPlan objects.", prefix="plan:")


class ReflectionSignature(dspy.Signature):
    """
    Assess the results of the executed plan against the original query and chat history.
    Decide if the information is sufficient, if replanning is needed, or if we can proceed to synthesize an answer.
    """
    # Input fields
    original_user_query = dspy.InputField(desc="The user's original question for this turn.")
    chat_history = dspy.InputField(desc="The overall conversation history.", T=dspy.History)
    executed_plan = dspy.InputField(desc="The plan that was just executed in the current iteration.")
    execution_log_and_results = dspy.InputField(desc="Log of tool calls and their outputs/errors from the recent execution.")

    # Output fields
    assessment_thought: str = dspy.OutputField(desc="Detailed reasoning about the sufficiency, relevance, and quality of the gathered information in relation to the user's query. Identify gaps or issues.")
    next_step_decision: Literal['ANSWER_WITH_SYNTHESIS', 'REPLAN_AND_EXECUTE'] = dspy.OutputField(desc="Choose one: 'ANSWER_WITH_SYNTHESIS' (if info is sufficient or max attempts reached), or 'REPLAN_AND_EXECUTE' (if more/different actions are needed).")
    guidance_for_next_step: str = dspy.OutputField(desc="If 'REPLAN_AND_EXECUTE', provide specific feedback/suggestions for the planner. If 'ANSWER_WITH_SYNTHESIS', briefly note key points to focus on for the synthesizer or confirm sufficiency.")

class SynthesizeResponseSignature(dspy.Signature):
    """
    Given the original query, chat history, the final plan, the log of tool actions and their outputs,
    and retrieved information, synthesize a comprehensive final answer for the user.
    If the retrieved information is insufficient, note what's missing.
    """
    # Input fields
    original_user_query = dspy.InputField(desc="The user's original question.")
    chat_history = dspy.InputField(desc="The history of the conversation.", T=dspy.History)
    plan_taken = dspy.InputField(desc="The final plan or sequence of plans that were executed.")
    execution_log_and_results = dspy.InputField(desc="Accumulated log of tools called and their outputs or observations.")
    retrieved_information = dspy.InputField(desc="All relevant information gathered through tool execution.")
    synthesis_guidance_from_reflector = dspy.InputField(desc="Any specific guidance or notes from the reflection step to aid in synthesis.")

    # Output fields
    thought_synthesis: str = dspy.OutputField(desc="Step-by-step thinking to synthesize the final answer from the gathered information.")
    final_answer: str = dspy.OutputField(desc="The comprehensive answer to the user.")