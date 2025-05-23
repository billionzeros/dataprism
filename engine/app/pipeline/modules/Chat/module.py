import re
import logging
import uuid
import dspy
from typing import List
from app.utils import APP_LOGGER_NAME
from ._schema import PlanQuerySignature, ReflectionSignature, SynthesizeResponseSignature

logger = logging.getLogger(APP_LOGGER_NAME)

class ChatModule(dspy.Module):
    """
    ChatModule is a class that represents a chat module in the application.
    It is responsible for handling chat-related operations and interactions.
    """

    def __init__(self, chat_id: uuid.UUID, tools: List[dspy.Tool], max_thinking_iterations: int = 5, **kwargs):
        super().__init__(**kwargs)

        self._chat_id = chat_id
        """
        Unique identifier for the chat session.
        """

        self._available_tools = {tool.name: tool for tool in tools}
        """
        Accessible tools for the chat module.
        """

        self._max_thinking_iterations = max_thinking_iterations
        """
        Maximum number of iterations for the thinking process.
        This is used to limit the number of times the module can think about a problem before going to the synthesizer.
        This is useful to avoid infinite loops or excessive thinking time.
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
        Description of the available tools in the chat module,
        which is used to inform the LLM about the tools that can be used.
        """
    
    @property
    def chat_id(self) -> uuid.UUID:
        """
        Get the unique identifier for the chat session.
        
        Returns:
            uuid.UUID: The unique identifier for the chat session.
        """
        return self._chat_id
    
    @property
    def history(self):
        """
        Get the history of the chat module.
        
        Returns:
            dspy.History: The history of the chat module.
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
        Generate a description of the tools available in the chat module.        
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
    

    def _parse_and_execute_tool_call(self, action_str: str):
        """
        Parse and Execute a tool call from the action string.
        This method is responsible for executing the tool call and returning the result, which the LLM is expected to use in the next step.
        The action string is expected to be in the format: 'call_tool(<tool_name>, <tool_input>)'.
        If the action string is not in the expected format, an error is raised.

        Args:
            action_str (str): The action string to parse and execute.
        
        Returns:
            Any: The result of the executed tool call.
        """
        match = re.match(r"call_tool\((\w+),\s*(.+)\)", action_str)

        if not match: 
            return {"error": "Invalid tool call format", "output": None}
        
        tool_name, tool_input, args_str = match.groups()

        if tool_name not in self._available_tools: 
            return {"error": f"Tool '{tool_name}' not found", "output": None}
        

        tool = self._available_tools[tool_name]
        tool_args = {}

        try:
            arg_match = re.match(r"(\w+)\s*=\s*\"(.*?)\"", args_str)

            if arg_match:
                arg_name, arg_value = arg_match.groups()
                tool_args[arg_name] = arg_value

            else:
                if tool.args:
                    tool_args = {k: v for k, v in zip(tool.args.keys(), args_str.split(","))}

            logger.info(f"Executing tool '{tool_name}' with args: {tool_args}")
            result = tool.func(**tool_args)

            return {"tool_name": tool_name, "args": tool_args, "output": result}

        except Exception as e:
            logger.error(f"Error executing tool '{tool_name}': {e}")

            return {"tool_name": tool_name, "args": tool_args, "error": str(e)}
        
    def forward(self, user_query: str, **kwargs):
        accumulated_execution_log_str = ""
        """
        Accumulated log of tool calls and their outputs/errors from the recent execution.
        """
        accumulated_retrieved_info_str = ""
        """
        All relevant information gathered through tool execution.
        """
        current_plan_str = "No plan yet."
        """
        Current plan of action, which is a list of actions to be taken.
        """
        feedback_for_planner = "No feedback provided."
        """
        Feedback for the planner, which is used to improve the planning process.
        """

        # Plans the thoughts after each iteration
        turn_thought_log = {
            "iterations": [],
        }

        for i in range(self._max_thinking_iterations):
            iteration_log: dict[str, str | int] = {"iteration": i + 1}

            logger.info(f"Thinking iteration {i + 1} of {self._max_thinking_iterations}")
            logger.info("Stage 1: Planning")

            planner_input = {
                "user_query": user_query,
                "chat_history": self._history,
                "available_tools_desc": self._tools_desc,
            }

            if feedback_for_planner:
                planner_input["feedback_on_previous_attempt"] = feedback_for_planner
            
            try:
                planner_output = self._planner(**planner_input)
                # Plan should be List[str] as per PlanQuerySignature
                current_plan: List[str] = planner_output.plan
                if not isinstance(current_plan, list) or not all(isinstance(item, str) for item in current_plan):
                    logger.warning(f"Planner output 'plan' is not a List[str]: {current_plan}. Attempting to use as is or correct.")
                    if isinstance(current_plan, str):
                            current_plan = [current_plan]
                    elif not isinstance(current_plan, list):
                            current_plan = [str(current_plan)]
                    else:
                            current_plan = [str(item) for item in current_plan]

            except Exception as e:
                logger.error(f"Error during Planner stage: {e}", exc_info=True)
                iteration_log["planning_error"] = str(e)
                turn_thought_log["iterations"].append(iteration_log)
                final_answer = "I encountered an issue while planning how to respond. Please try rephrasing your query."
                return dspy.Prediction(final_answer=final_answer, full_thought_process=turn_thought_log)

            logger.info("Stage 2: Reflection")
            current_execution_log_entries = []
            current_retrieved_info_list = []

            if current_plan:
                logger.info("Executing plan...", )
                for action in current_plan:
                    logger.info(f"Executing action: {action}")
                    if action.startswith("call_tool"):
                        tool_result = self._parse_and_execute_tool_call(action)
                        current_execution_log_entries.append(tool_result)
                        if tool_result.get("output"):
                            current_retrieved_info_list.append(str(tool_result["output"]))

                        elif tool_result.get("error"):
                            current_retrieved_info_list.append(f"Error from {tool_result.get('tool_name','unknown tool')}: {tool_result['error']}")

                    elif action.startswith("answer_directly"):
                        direct_answer_content = action.replace("answer_directly(", "")[:-1].strip('"').strip("'")
                        log_entry = f"Action: answer_directly. Content: {direct_answer_content}"
                        current_execution_log_entries.append(log_entry)
                        current_retrieved_info_list.append(f"Planner decided to answer directly: {direct_answer_content}")
                    
                    else:
                        current_execution_log_entries.append(f"Unknown action: {action}")
            else:
                current_execution_log_entries.append("Planner generated an empty plan.")

            current_execution_log_str = "\n".join(current_execution_log_entries)
            iteration_log["execution_log"] = current_execution_log_str
            accumulated_execution_log_str += f"\n--- Iteration {i+1} Execution ---\n" + current_execution_log_str
            accumulated_retrieved_info_str += "\n" + "\n".join(current_retrieved_info_list) if current_retrieved_info_list else ""
            logger.info(f"Execution Log (Iter {i+1}):\n{current_execution_log_str}")

            if any(action.startswith("answer_directly") for action in current_plan) and i == 0 and not any(action.startswith("call_tool") for action in current_plan):
                logger.info("Planner suggests direct answer without tool use, moving to Synthesis.")
                iteration_log["reflection_thought"] = "Skipped due to direct answer plan."
                iteration_log["next_step_decision"] = "ANSWER_WITH_SYNTHESIS" # Force synthesis
                iteration_log["guidance_for_next_step"] = "Synthesize based on planner's direct answer."
                turn_thought_log["iterations"].append(iteration_log)
                break

            # Check and understand based on the Reflection from the outputs generated by the Tool_Call
            # And understand if we have a need to replan or not.
            if i < self._max_thinking_iterations - 1:
                logger.info("Stage 3: Reflection")
                reflection_input = {
                    "original_user_query": user_query,
                    "chat_history": self._history,
                    "executed_plan": current_plan_str,
                    "execution_log_and_results": accumulated_execution_log_str,
                }

                reflector_output = self._reflector(**reflection_input)

                iteration_log["reflection_thought"] = reflector_output.assessment_thought
                iteration_log["next_step_decision"] = reflector_output.next_step_decision
                iteration_log["guidance_for_next_step"] = reflector_output.guidance_for_next_step

                logger.info(f"Reflection thought: {reflector_output.assessment_thought}")
                logger.info(f"Next step decision: {reflector_output.next_step_decision}")
                logger.info(f"Guidance for next step: {reflector_output.guidance_for_next_step}")

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
            "plan_taken": current_plan_str,
            "execution_log_and_results": accumulated_execution_log_str,
            "retrieved_information": accumulated_retrieved_info_str,
            "synthesis_guidance_from_reflector": turn_thought_log["iterations"][-1].get("guidance_for_next_step", "Synthesize the best possible answer with available information."),
        }

        logger.info(f"Synthesis input: {synthesis_input}")

        synthesis = self._synthesizer(**synthesis_input)

        logger.info(f"Final Synthesis: {synthesis}")

        final_answer = str(synthesis.final_answer)

        logger.info(f"Synthesizer Thought: {synthesis.thought_synthesis}")
        logger.info(f"Final Answer: {final_answer}")


        return dspy.Prediction(
            final_answer=final_answer,
            thought_process=turn_thought_log,
            thought_synthesis=synthesis.thought_synthesis,
        )