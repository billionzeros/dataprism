import dspy
from app.pipeline._schema import FinalResult


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