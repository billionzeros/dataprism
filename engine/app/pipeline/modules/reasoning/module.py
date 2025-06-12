import logging
import uuid
import mlflow
import dspy
from typing import List
from app.utils import APP_LOGGER_NAME
from app.pipeline._schema import FinalResult, Paragraph
from ._signatures import SynthesizeResponseSignature

logger = logging.getLogger(APP_LOGGER_NAME)


# Custom Signature to explicitly guide the ReAct agent's reasoning and stopping condition.
class AgenticSignature(dspy.Signature):
    """
    You are a helpful assistant. You have access to a suite of tools.
    Your mission is to answer the user's question by reasoning step-by-step.
    """
    question = dspy.InputField(desc="The user's question, potentially with chat history for context.")


class ReasoningModule(dspy.Module):
    """
    ReasoningModule is a class that orchestrates an AI agent to answer a query.
    It uses a custom-guided dspy.ReAct module to iteratively use tools and then 
    synthesizes a final, polished response.
    """

    def __init__(self, session_id: uuid.UUID, tools: List[dspy.Tool], max_thinking_iterations: int = 5, **kwargs):
        super().__init__(**kwargs)

        self._session_id = session_id
        """Unique identifier for the ReasoningModule instance."""

        self._agent = dspy.ReAct(
            signature=AgenticSignature,
            tools=tools,
            max_iters=max_thinking_iterations
        )
        """
        The core agent that reasons and acts using the provided tools, guided by AgenticSignature.
        """
        
        self._synthesizer = dspy.ChainOfThought(SynthesizeResponseSignature)
        """
        Responsible for the synthesis of the final answer based on the agent's work.
        """
        
        self._history = dspy.History(messages=[])
        """History for all the Messages in the Chat."""

    @property
    def session_id(self) -> uuid.UUID:
        """Get the unique identifier for the session."""
        return self._session_id
    
    @property
    def history(self):
        """Get the history of the module."""
        return self._history

    async def aforward(self, user_query: str, **kwargs):
        """
        Asynchronously executes the agentic workflow.

        1. Calls the ReAct agent (guided by AgenticSignature) to use tools and gather information.
        2. Feeds the agent's process into a synthesizer to generate a final, polished answer.
        """
        logger.info(f"Starting ReAct agent for user query: '{user_query}'")
        
        with mlflow.start_run():
            mlflow.set_tag("module_name", self.__class__.__name__)

            try:
                # Combine history and current query for full context, as suggested by the signature.
                contextual_query = f"Chat History:\n{self._history}\n\nUser Query: {user_query}"

                # The agent will now follow the more explicit logic from AgenticSignature.
                agent_result = await self._agent.acall(question=contextual_query)
                
                # The full thought process is available in the dspy history.
                full_thought_process = dspy.settings.lm.history
                
                # The ReAct module, when it stops, places the final answer in the 'answer' attribute.
                agent_final_answer = agent_result.answer

                # Create a structured execution log for the synthesizer.
                execution_log = "\n\n".join([
                    f"Thought: {h['prompt']}\n\nResponse: {h['response']}"
                    for h in full_thought_process
                    if 'rationale' in h 
                ])

            except Exception as e:
                logger.error(f"Error during ReAct Agent execution: {e}", exc_info=True)
                final_answer = "I encountered an issue while trying to figure out how to respond. Please try rephrasing your query."
                return dspy.Prediction(
                    answer=[Paragraph(type="paragraph", text=final_answer)],
                    reasoning="Agent execution failed.",
                    thought_process=str(e),
                )

            logger.info("ReAct agent finished. Moving to Synthesis stage.")
            
            # The agent has produced its own final answer. We now use the synthesizer
            # to ensure it's in the correct final format (e.g., FinalResult schema).
            synthesis_input = {
                "original_user_query": user_query,
                "chat_history": self._history,
                "plan_reasoning": "The ReAct agent determined the plan and stopping point internally based on its instructions.",
                "execution_log_and_results": execution_log,
                "synthesis_guidance_from_reflector": f"Synthesize a final response based on the agent's findings. The agent's raw answer was: '{agent_final_answer}'",
            }

            logger.info(f"Synthesis input keys: {list(synthesis_input.keys())}")
            
            try:
                synthesis = self._synthesizer(**synthesis_input)
                logger.info(f"Final Synthesis: {synthesis}")

                result = synthesis.final_result
                
                if not isinstance(result, FinalResult):
                        logger.error(f"Expected FinalResult, but got {type(result)}. Falling back to agent's raw answer.")
                        result = FinalResult(results=[Paragraph(type="paragraph", text=str(agent_final_answer))])

                return dspy.Prediction(
                    answer=result.results,
                    reasoning=synthesis.reasoning,
                    thought_process=full_thought_process,
                )

            except Exception as e:
                logger.error(f"Error during Synthesizer stage: {e}", exc_info=True)
                
                result = FinalResult(
                    results=[Paragraph(type="paragraph", text="An error occurred during the final response generation.")],
                )

                return dspy.Prediction(
                    answer=result.results,
                    reasoning="An error occurred during synthesis.",
                    thought_process=full_thought_process,
                )
