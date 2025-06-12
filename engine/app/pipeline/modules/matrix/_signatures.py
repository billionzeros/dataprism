import dspy
from typing import List, Literal, Optional, Union
from ._schema import ToolActionPlan, DirectAnswerActionPlan, ToolExecutionResult
from app.pipeline._schema import FinalResult


class PlanQuerySignature(dspy.Signature):
    """
    Given the user query, chat history, available tools, and optional feedback from a previous attempt,
    understand the query, create a step-by-step plan, and identify tool calls (ToolActionPlan) or direct answer (DirectAnswerActionPlan)
    Plan actions: 'call_tool(<tool_name>, <tool_input>)' or 'answer_directly(<summary>)'.
    """
    # Input fields
    user_query: str = dspy.InputField(desc="The user's current question or statement.")
    chat_history = dspy.InputField(desc="The history of the conversation.", T=dspy.History)
    available_tools_desc = dspy.InputField(desc="Description of available tools.")

    previous_execution_results: str = dspy.InputField(
        desc="Results of tool calls and their outputs/errors from the previous execution steps. This is used to track the progress and results of the plan execution, results are appended in the order of the plan execution.",
    )

    feedback_on_previous_attempt = dspy.InputField(desc="Optional feedback from a previous execution cycle for this query.")
    
    # Output fields
    plan: List[DirectAnswerActionPlan | ToolActionPlan] = dspy.OutputField(desc="List of structured actions to execute as per the defined format, This should be a valid JSON list of ActionPlan objects.", prefix="plan:")


class ExecutePlanSignature(dspy.Signature):
    """
    Execute the Tool Call in Provided Plan Step-by-Step, based on the provided result of the previous tool call,
    return the next_action to be executed, fix the args if needed because its possible that the args of the tool call need depends on the result of the previous tool call.
    if all the tool calls in the plan are executed, return finished=True and the final result of the plan execution, will be considered as the final result of the plan execution.

    If the next_action according to plan is DirectAnswerActionPlan, it should return that as the next_action
    """
    plan: List[DirectAnswerActionPlan | ToolActionPlan] = dspy.InputField(
        desc="The plan to execute, which is a list of DirectAnswerActionPlan or ToolActionPlan objects. This should be a valid JSON list of ActionPlan objects.",
        T=List[Union[DirectAnswerActionPlan, ToolActionPlan]]
    )

    available_tools_desc: str = dspy.InputField(
        desc="Description of available tools that can be used in the plan execution. This is used to understand which tools are available for the tool calls in the plan.",
        T=str
    )

    action_results: List[ToolExecutionResult] = dspy.InputField(
        desc="Results of tool calls and their outputs/errors from the previous execution steps. This is used to track the progress and results of the plan execution, results are appended in the order of the plan execution.",
    )

    # Output fields
    next_action: Optional[Union[DirectAnswerActionPlan, ToolActionPlan]] = dspy.OutputField(
        desc="The next action to be executed from the plan. It can be a DirectAnswerActionPlan (if the answer is ready) or a ToolActionPlan (if a tool needs to be called). If all actions are executed, this will be None.",
        prefix="next_action:",
        T=Union[DirectAnswerActionPlan, ToolActionPlan]
    )

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

    Important:
    - Final Result Follows the format as suggested in your Reasoning.
    """
    # Input fields
    original_user_query = dspy.InputField(desc="The user's original question.")
    chat_history = dspy.InputField(desc="The history of the conversation.", T=dspy.History)
    plan_reasoning = dspy.InputField(desc="The reasoning behind the plan that was executed, including the thought process and decisions made during planning.")
    execution_log_and_results = dspy.InputField(desc="Accumulated log of tools called and their outputs or observations.")
    synthesis_guidance_from_reflector = dspy.InputField(desc="Any specific guidance or notes from the reflection step to aid in synthesis.")

    # Output fields
    final_result: FinalResult = dspy.OutputField(desc="The comprehensive answer to the user.")
