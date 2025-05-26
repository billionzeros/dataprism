import dspy
from typing import List, Literal, Optional, Union, Any
from ._schema import FinalResult, ToolActionPlan, DirectAnswerActionPlan, ToolExecutionResult


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


class ExecutePlanSignature(dspy.Signature):
    """
    Execute the Tool Call in Provided Plan Step-by-Step, based on the provided result of the previous tool call,
    return the next_action to be executed, fix the args if needed because its possible that the args of the tool call need depends on the result of the previous tool call.
    if all the tool calls in the plan are executed, return finished=True and the final result of the plan execution, will be considered as the final result of the plan execution.

    If the next function according to plan is answer_directly, it should return the answer_text as the final result of the plan execution.
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

    # state: Literal['finishied', 'executing'] = dspy.OutputField(
    #     desc="Indicates whether the plan execution is finished. 'finished' means all actions are executed and the final result is ready, 'executing' means there are still actions to be executed.",
    #     prefix="state:",
    #     T=Literal['finished', 'executing']
    # )

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
    final_result: FinalResult = dspy.OutputField(desc="The comprehensive answer to the user.")
