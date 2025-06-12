import logging
import uuid
import inspect
import dspy
from typing import List, Any
from app.utils import APP_LOGGER_NAME
from ._schema import ToolExecutionResult, ToolActionPlan, DirectAnswerActionPlan
from app.pipeline._schema import FinalResult, Paragraph
from ._signatures import PlanQuerySignature, ReflectionSignature, SynthesizeResponseSignature, ExecutePlanSignature

logger = logging.getLogger(APP_LOGGER_NAME)

class MatrixModule(dspy.Module):
    """
    MatrixModule is a class that handles LLM based execution of the query sent to the matrix.
    """

    def __init__(self, session_id: uuid.UUID, tools: List[dspy.Tool], max_thinking_iterations: int = 5, **kwargs):
        super().__init__(**kwargs)

        self._session_id = session_id
        """
        Unique identifier for the ExecutionModule instance.
        """

        self._available_tools: dict[str, dspy.Tool] = {str(tool.name): tool for tool in tools}
        """
        Accessible tools for the Module.
        """

        self._max_thinking_iterations = max_thinking_iterations
        """
        Maximum number of iterations for the thinking process.
        This is used to limit the number of times the module can think about a problem before going to the synthesizer.
        This is useful to avoid infinite loops or excessive thinking time.
        """

        self._max_tools_calls = 10
        """
        Maximum number of tool calls that can be made in a single thinking iteration.
        """

        self._history = dspy.History(messages=[])
        """
        History for all the Messages in the Chat
        """

        # sub-modules
        self._planner = dspy.ChainOfThought(PlanQuerySignature)
        """
        Responsible for the first interation with the user and plan the next step of answer it the best way possible
        """

        self._execution = dspy.Predict(ExecutePlanSignature)
        """
        Execution module that handles the execution of the tools based on the actions planned by the planner.
        It is responsible for executing the tools and returning the results.
        """

        self._reflector = dspy.ChainOfThought(ReflectionSignature)
        """
        Responsible for the reflection of the last step and decide if we need to replan or not
        """

        self._synthesizer = dspy.ChainOfThought(SynthesizeResponseSignature)
        """
        Responsible for the synthesis of the final answer 
        """

        self._tools_desc = self._generate_tools_description()
        """
        Description of the available tools in the module,
        which is used to inform the LLM about the tools that can be used.
        """
    
    @property
    def session_id(self) -> uuid.UUID:
        """
        Get the unique identifier for the session.
        
        Returns:
            uuid.UUID: The unique identifier for the session.
        """
        return self._session_id
    
    @property
    def history(self):
        """
        Get the history of the module.
        
        Returns:
            dspy.History: The history of the module.
        """
        return self._history
    
    @property
    def max_thinking_iterations(self) -> int:
        """
        Get the maximum number of iterations for the thinking process.
        
        Returns:
            int: The maximum number of iterations for the thinking process.
        """
        return self._max_thinking_iterations

    def _generate_tools_description(self) -> str:
        """
        Generate a description of the tools available in the module.        
        """
        descriptions = []
        for tool_name, tool_instance in self._available_tools.items():
            # Tool Description
            tool_desc = tool_instance.desc or "No description available."
            """
            desc (Optional[str], optional): The description of the tool. Defaults to None.
            """

            # Input Signature
            tool_args = tool_instance.args or {}
            """
            args (Optional[dict[str, Any]], optional): The args and their schema of the tool, represented as a
                dictionary from arg name to arg's json schema. Defaults to None.
            """

            # Tool Input Signature Type
            tool_args_types = tool_instance.arg_types or {}
            """
            arg_types (Optional[dict[str, Any]], optional): The argument types of the tool, represented as a dictionary
                from arg name to the type of the argument. Defaults to None.
            """

            # Tool Input Signature Description
            tool_args_desc = tool_instance.arg_desc or {}
            """
            arg_desc (Optional[dict[str, str]], optional): Descriptions for each arg, represented as a
                dictionary from arg name to description string. Defaults to None.
            """

            descriptions.append(f"Tool: {tool_name}\nDescription: {tool_desc}\nInput Signature: {tool_args}\nInput Signature Type: {tool_args_types}\nInput Signature Description: {tool_args_desc}\n")

        return "\n".join(descriptions) if descriptions else "No tools available."
    
    async def _parse_and_execute_tool_call(self, action: ToolActionPlan) -> ToolExecutionResult:
        """
        Parse and Execute a Tool based on the action provided in the function and return the result.

        Args:
            action: The Definination of the Tool Action
        
        Returns:
            Any: The result of the executed tool call.
        """
        if action.tool_name not in self._available_tools: 
            logger.error(f"Tool '{action.tool_name}' not found. Available tools: {list(self._available_tools.keys())}")
            return ToolExecutionResult(
                tool_name=action.tool_name,
                tool_args=action.tool_args,
                result=None,
                error=f"Tool '{action.tool_name}' not found in available tools."
            )
        
        tool = self._available_tools[action.tool_name]
        tool_args: dict[str, Any] = {}

        try:
            if isinstance(action.tool_args, dict):
                tool_args = action.tool_args
            
            elif action.tool_args is not None and not isinstance(action.tool_args, dict):
                logger.warning(
                    f"Tool '{action.tool_name}' received tool_args as a string: '{action.tool_args}'. "
                    f"This system expects tool arguments as a dictionary for keyword passing. "
                    f"Attempting to call tool without keyword arguments. If the tool expects this string as a named argument, "
                    f"the plan should specify it as a dictionary (e.g., {{'input_arg_name': '{action.tool_args}'}})."
                )

            logger.info(f"Executing tool '{action.tool_name}' with args: {tool_args}")

            result = None
            if not inspect.isfunction(tool.func) and not inspect.ismethod(tool.func):
                logger.error(f"Tool '{action.tool_name}' does not have a callable function. It is likely not properly registered.")
                return ToolExecutionResult(
                    tool_name=action.tool_name,
                    tool_args=tool_args,
                    result=None,
                    error=f"Tool '{action.tool_name}' does not have a callable function."
                )

            if inspect.iscoroutinefunction(tool.func) or inspect.isawaitable(tool.func):
                logger.info(f"Tool '{action.tool_name}' is an async function, awaiting execution.")
                result = await tool.func(**tool_args)
            else:
                logger.info(f"Tool '{action.tool_name}' is a sync function, calling directly.")
                result = tool.func(**tool_args)

            return ToolExecutionResult(
                tool_name=action.tool_name,
                tool_args=tool_args,
                result=result,
                error=None
            )

        except Exception as e:
            logger.error(f"Error executing tool '{action}': {e}")

            return ToolExecutionResult(
                tool_name=action.tool_name,
                tool_args=tool_args,
                result=None,
                error=str(e)
            )
        
    async def aforward(self, user_query: str, **kwargs):
        accumulated_execution_log_str = ""
        """
        Accumulated log of tool calls and their outputs/errors from the recent execution.
        """
        feedback_for_planner = "No feedback provided."
        """
        Feedback for the planner, which is used to improve the planning process.
        """

        plan_reasoning = "No reasoning provided."
        """
        Reasoning for the plan, which is used to understand the planner's thought process.
        This is used to provide context for the planner's decisions and actions.
        """

        # Plans the thoughts after each iteration
        turn_thought_log = {
            "iterations": [],
        }

        for i in range(self._max_thinking_iterations):
            iteration_log: dict[str, str | int] = {"iteration": i + 1}
            execution_results: List[Any] = []


            logger.info(f"Thinking iteration {i + 1} of {self._max_thinking_iterations}")
            logger.info("Stage 1: Planning")

            planner_input = {
                "user_query": user_query,
                "chat_history": self._history,
                "previous_execution_results": accumulated_execution_log_str,
                "available_tools_desc": self._tools_desc,
            }

            if feedback_for_planner:
                planner_input["feedback_on_previous_attempt"] = feedback_for_planner
            
            try:
                planner_output = self._planner(**planner_input)
                current_plan: List[ToolActionPlan | DirectAnswerActionPlan] = planner_output.plan
                plan_reasoning = planner_output.reasoning

            except Exception as e:
                logger.error(f"Error during Planner stage: {e}", exc_info=True)
                iteration_log["planning_error"] = str(e)
                turn_thought_log["iterations"].append(iteration_log)
                final_answer = "I encountered an issue while planning how to respond. Please try rephrasing your query."
                return dspy.Prediction(final_answer=final_answer, full_thought_process=turn_thought_log)

            logger.info(f"Current Plan (Iter {i+1}): {current_plan}")


            logger.info("Stage 2: Reflection")
            if any(isinstance(action, DirectAnswerActionPlan) for action in current_plan) and i == 0 and not any(isinstance(action, ToolActionPlan) for action in current_plan):
                logger.info("Planner suggests direct answer without tool use, moving to Synthesis.")
                
                iteration_log["reflection_thought"] = "Skipped due to direct answer plan."
                iteration_log["next_step_decision"] = "ANSWER_WITH_SYNTHESIS"
                iteration_log["guidance_for_next_step"] = "Synthesize based on planner's direct answer."
                turn_thought_log["iterations"].append(iteration_log)
                break

            if current_plan:
                logger.info("Executing plan...", )
                
                execution_input = {
                    "plan": current_plan,
                    "available_tools_desc": self._tools_desc,
                    "action_results": execution_results,
                }

                finished = False
                while not finished:
                    if len(execution_results) >= self._max_tools_calls:
                        logger.warning(f"Reached maximum tool calls limit ({self._max_tools_calls}). Stopping execution.")
                        execution_results.append(f"Reached maximum tool calls limit, max_tool_calls = {self._max_tools_calls}")
                        break

                    execution_output = self._execution(**execution_input)
                    next_action = execution_output.next_action

                    if next_action is None:
                        logger.info("All actions in the plan have been executed.")
                        finished = True
                        break

                    if isinstance(next_action, ToolActionPlan):
                        tool_result = await self._parse_and_execute_tool_call(execution_output.next_action)
                        execution_results.append(tool_result)

                        if tool_result.error:
                            logger.error(f"Error Executing tool '{tool_result.tool_name}': {tool_result.error}")
                            execution_results.append(f"Error executing tool '{tool_result.tool_name}': {tool_result.error}")
                            finished = True
                            break

                    elif isinstance(next_action, DirectAnswerActionPlan):
                        log_entry = f"Action: answer_directly. Content: {next_action.answer_text}"
                        execution_results.append(log_entry)                
                    else:
                        logger.error(f"Unknown action type: {next_action}")
                        execution_results.append(f"Unknown action: {next_action}")
            else:
                logger.error("Planner generated an empty plan.")
                execution_results.append("Planner generated an empty plan.")

            execution_result_str = "\n".join(
                f"Tool: {result.tool_name}, Args: {result.tool_args}, Result: {result.result}, Error: {result.error}"
                for result in execution_results if isinstance(result, ToolExecutionResult)
            )

            # Accumulate retrieved information for future steps
            iteration_log["execution_log"] = execution_result_str
            accumulated_execution_log_str += f"\n--- Iteration {i+1} Execution ---\n" + execution_result_str

            if i < self._max_thinking_iterations - 1:
                logger.info("Stage 3: Reflection")
                reflection_input = {
                    "original_user_query": user_query,
                    "chat_history": self._history,
                    "executed_plan": str(current_plan),
                    "execution_log_and_results": accumulated_execution_log_str,
                }

                reflector_output = self._reflector(**reflection_input)
                logger.info(f"Reflection Assessment Output: {reflector_output}")
                
                # Logging the reflection output
                iteration_log["reflection_thought"] = reflector_output.assessment_thought
                iteration_log["next_step_decision"] = reflector_output.next_step_decision
                iteration_log["guidance_for_next_step"] = reflector_output.guidance_for_next_step


                if reflector_output.next_step_decision == "ANSWER_WITH_SYNTHESIS":
                        logger.info("ANSWER_WITH_SYNTHESIS decision made, moving to Synthesis.")
                        turn_thought_log["iterations"].append(iteration_log)
                        break
                
                elif reflector_output.next_step_decision == "REPLAN_AND_EXECUTE":
                    logger.info("REPLAN_AND_EXECUTE decision made, re-planning.")
                    feedback_for_planner = reflector_output.guidance_for_next_step

                else:
                    logger.warning(f"Unknown reflector decision: {reflector_output.next_step_decision}. Breaking loop.")
                    turn_thought_log["iterations"].append(iteration_log)
                    break

            else:
                logger.info("Max iterations reached, moving to Synthesis.")
                iteration_log["reflection_thought"] = "Max iterations reached."
                iteration_log["next_step_decision"] = "ANSWER_WITH_SYNTHESIS"
                iteration_log["guidance_for_next_step"] = "Synthesize based on the gathered information."

            turn_thought_log["iterations"].append(iteration_log)

        logger.info("Stage 4: Synthesis")
        synthesis_input = {
            "original_user_query": user_query,
            "chat_history": self._history,
            "plan_reasoning": plan_reasoning,
            "execution_log_and_results": accumulated_execution_log_str,
            "synthesis_guidance_from_reflector": turn_thought_log["iterations"][-1].get("guidance_for_next_step", "Synthesize the best possible answer with available information."),
        }

        logger.info(f"Synthesis input: {synthesis_input}")

        synthesis = self._synthesizer(**synthesis_input)

        logger.info(f"Final Synthesis: {synthesis}")

        result = synthesis.final_result

        if not result:
            logger.warning("Synthesis did not return a final result. Returning a default message.")
            result = FinalResult(
                results=[Paragraph(type= "paragraph", text="No valid result was synthesized. Please try rephrasing your query.")],
            )

        if not isinstance(result, FinalResult):
            logger.error(f"Expected FinalResult, but got {type(result)}. Returning a default message.")
            result = FinalResult(
                results=[Paragraph(type= "paragraph", text="An error occurred during synthesis. Please try rephrasing your query.")],
            )

        return dspy.Prediction(
            answer=result.results,
            reasoning=synthesis.reasoning,
            thought_process=turn_thought_log,
        )
    
    