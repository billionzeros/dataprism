import dspy
from typing import List
class PlanQuerySignature(dspy.Signature):
    """
    Given the user query, chat history, available tools, and optional feedback from a previous attempt,
    understand the query, create a step-by-step plan, and identify tool calls.
    Plan actions: 'call_tool(<tool_name>, <tool_input>)' or 'answer_directly(<summary>)'.
    """
    # Input fields
    user_query = dspy.InputField(desc="The user's current question or statement.")
    chat_history = dspy.InputField(desc="The history of the conversation.", T=dspy.History)
    available_tools_desc = dspy.InputField(desc="Description of available tools.")
    feedback_on_previous_attempt = dspy.InputField(desc="Optional feedback from a previous execution cycle for this query.")
    
    # Output fields
    thought_plan = dspy.OutputField(desc="Step-by-step thinking process for the plan.", prefix="plan_thought:")
    plan: List[str]  = dspy.OutputField(desc="List of actions. E.g., ['call_tool(SearchEmbedding, query=\"topic\")'] or ['answer_directly(\"Hello!\")']", format="list[str]", prefix="plan:")


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
    assessment_thought = dspy.OutputField(desc="Detailed reasoning about the sufficiency, relevance, and quality of the gathered information in relation to the user's query. Identify gaps or issues.")
    next_step_decision = dspy.OutputField(desc="Choose one: 'ANSWER_WITH_SYNTHESIS' (if info is sufficient or max attempts reached), or 'REPLAN_AND_EXECUTE' (if more/different actions are needed).")
    guidance_for_next_step = dspy.OutputField(desc="If 'REPLAN_AND_EXECUTE', provide specific feedback/suggestions for the planner. If 'ANSWER_WITH_SYNTHESIS', briefly note key points to focus on for the synthesizer or confirm sufficiency.")

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
    thought_synthesis = dspy.OutputField(desc="Step-by-step thinking to synthesize the final answer from the gathered information.")
    final_answer = dspy.OutputField(desc="The comprehensive answer to the user.")