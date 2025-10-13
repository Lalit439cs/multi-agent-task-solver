import asyncio
import operator
from typing import Annotated, List, Tuple, Union, TypedDict, Any
import json

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_google_vertexai import ChatVertexAI
# from langchain_google_genai import ChatGoogleGenerativeAI

from langgraph.graph import StateGraph, END

from config import Config
from tools import PythonCodeExecutor, WebSearchTool, FileIOTool

# --- Define LangGraph State ---
class AgentState(TypedDict):
    """Represents the state of our agent throughout the conversation."""
    user_request: str
    chat_history: Annotated[List[BaseMessage], operator.add]
    plan: str
    subtasks: List[dict]
    current_subtask_index: int
    agent_results: List[dict]
    final_answer: str
    llm_model_preference: str # 'gpt4' or 'gemini'
    
# --- Define Tools ---
# These are actual tools that agents can use. LangGraph will manage their invocation.

@tool
def python_executor_tool(code: str) -> str:
    """Executes Python code in a sandboxed environment. Returns the output."""
    executor = PythonCodeExecutor()
    return executor.execute(code)

@tool
def web_search_tool(query: str) -> str:
    """Performs a web search for the given query and returns the search results."""
    searcher = WebSearchTool()
    return searcher.run(query)

@tool
def file_io_tool(action: str, path: str, content: str = None) -> str:
    """Performs file I/O operations (read, write, append)."""
    file_handler = FileIOTool()
    if action == "read":
        return file_handler.read(path)
    elif action == "write":
        return file_handler.write(path, content)
    elif action == "append":
        return file_handler.append(path, content)
    else:
        return "Invalid file I/O action."

# --- Define LLM Models ---
class LLMManager:
    def __init__(self, use_gpt4: bool, use_gemini: bool):
        self.gpt4 = None
        self.gemini = None
        self.available_models = []

        if use_gpt4 and Config.OPENAI_API_KEY:
            self.gpt4 = ChatOpenAI(model=Config.OPENAI_MODEL, temperature=0.3, openai_api_key=Config.OPENAI_API_KEY)
            self.available_models.append('gpt4')
        if use_gemini and Config.GOOGLE_API_KEY:
            # self.gemini = ChatGoogleGenerativeAI(model=Config.GEMINI_MODEL, temperature=0.3, google_api_key=Config.GOOGLE_API_KEY)
            self.gemini = ChatVertexAI(model=Config.GEMINI_MODEL, temperature=0.3, project_id=Config.GEMINI_PROJECT_ID)
            self.available_models.append('gemini')
        
        if not self.available_models:
            raise ValueError("No LLM models configured. Please provide at least one API key (OpenAI or Google Gemini).")

    def get_llm(self, preference: str = None):
        if preference == 'gpt4' and self.gpt4:
            return self.gpt4
        if preference == 'gemini' and self.gemini:
            return self.gemini
        
        # Default to the first available model if preference not met or not specified
        if self.gpt4:
            return self.gpt4
        if self.gemini:
            return self.gemini
        return None # Should not happen due to validation in __init__

# --- Define Agents (Nodes in LangGraph) ---
class MultiAgentOrchestrator:
    def __init__(self, use_gpt4: bool = True, use_gemini: bool = False):
        Config.validate() # Validate API keys
        self.llm_manager = LLMManager(use_gpt4, use_gemini)
        self.tools = [python_executor_tool, web_search_tool, file_io_tool]
        self.graph = self._build_graph()

    async def _call_llm_async(self, llm, prompt_template, state: AgentState):
        prompt = prompt_template.format_messages(
            user_request=state["user_request"],
            chat_history=state["chat_history"],
            plan=state["plan"],
            subtasks=state["subtasks"],
            agent_results=state["agent_results"]
        )
        response = await llm.ainvoke(prompt)
        return response.content

    async def _call_agent_llm_async(self, llm, system_message: str, user_message: str):
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("user", user_message)
        ])
        # Format the prompt to get the actual messages
        formatted_messages = prompt.format_messages()
        response = await llm.ainvoke(formatted_messages)
        return response.content

    async def _planner_node(self, state: AgentState, config_dict: dict = None):
        llm = self.llm_manager.get_llm(state["llm_model_preference"])
        if not llm:
            raise ValueError("No LLM available for planning.")

        planner_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a world-class task planning AI. Your job is to break down the user's request into clear, actionable subtasks.

CRITICAL: You MUST respond with ONLY a valid JSON array. No explanations, no markdown, no code blocks - ONLY the JSON array.

For each subtask, identify:
- subtask_description: A clear description of what needs to be done
- agent: Choose from 'summarizer', 'data_analyst', 'researcher', or 'code_executor'
- tools: A list of tool names (from 'python_executor_tool', 'web_search_tool', 'file_io_tool') or an empty list []

Response format (THIS IS THE ONLY VALID FORMAT):
[
    {{"subtask_description": "Search for latest AI advancements news", "agent": "researcher", "tools": ["web_search_tool"]}},
    {{"subtask_description": "Summarize key findings from AI advancements news", "agent": "summarizer", "tools": []}},
    {{"subtask_description": "Search for AI market growth statistics", "agent": "researcher", "tools": ["web_search_tool"]}},
    {{"subtask_description": "Analyze AI market growth data", "agent": "data_analyst", "tools": ["python_executor_tool"]}}
]

Remember: ONLY output the JSON array, nothing else."""),
            ("user", "User Request: {user_request}")
        ])
        
        formatted_messages = planner_prompt.format_messages(user_request=state["user_request"])
        response = await llm.ainvoke(formatted_messages)
        plan_str = response.content
        
        print(f"\n=== PLANNER RAW RESPONSE ===\n{plan_str}\n=== END RAW RESPONSE ===\n")
        
        try:
            # Clean up common LLM JSON formatting issues
            plan_str_cleaned = plan_str.strip()
            # Remove markdown code blocks
            if plan_str_cleaned.startswith('```'):
                lines = plan_str_cleaned.split('\n')
                # Remove first line if it's ```json or just ```
                if lines[0].strip() in ['```json', '```']:
                    lines = lines[1:]
                # Remove last line if it's ```
                if lines and lines[-1].strip() == '```':
                    lines = lines[:-1]
                plan_str_cleaned = '\n'.join(lines)
            
            print(f"\n=== CLEANED JSON STRING ===\n{plan_str_cleaned}\n=== END CLEANED ===\n")
            
            subtasks = json.loads(plan_str_cleaned)
            
            print(f"\n=== PARSED SUBTASKS ===\n{json.dumps(subtasks, indent=2)}\n=== END PARSED ===\n")
            
            # Validate the parsed subtasks
            if not isinstance(subtasks, list):
                raise ValueError(f"Expected a list of subtasks, got {type(subtasks).__name__}: {subtasks}")
            
            if len(subtasks) == 0:
                raise ValueError("No subtasks generated in the plan")
            
            # Validate each subtask has required fields
            for i, subtask in enumerate(subtasks):
                if not isinstance(subtask, dict):
                    raise ValueError(f"Subtask {i} is not a dict, got {type(subtask).__name__}: {repr(subtask)}")
                required_keys = ["subtask_description", "agent", "tools"]
                missing = [k for k in required_keys if k not in subtask]
                if missing:
                    raise ValueError(f"Subtask {i} missing keys: {missing}. Got keys: {list(subtask.keys())}. Full subtask: {subtask}")
            
            return {"plan": plan_str, "subtasks": subtasks, "current_subtask_index": 0}
        except json.JSONDecodeError as e:
            error_msg = f"JSON decoding error: {str(e)}\nRaw response: {plan_str}\nCleaned response: {plan_str_cleaned if 'plan_str_cleaned' in locals() else 'N/A'}"
            print(f"\n!!! {error_msg}\n")
            raise ValueError(error_msg)
        except ValueError as e:
            error_msg = f"Validation error: {str(e)}\nRaw response: {plan_str}"
            print(f"\n!!! {error_msg}\n")
            raise ValueError(error_msg)

    async def _agent_executor_node(self, state: AgentState, config_dict: dict = None):
        llm = self.llm_manager.get_llm(state["llm_model_preference"])
        if not llm:
            raise ValueError("No LLM available for agent execution.")

        current_subtask_index = state["current_subtask_index"]
        if current_subtask_index >= len(state["subtasks"]):
            return state # All subtasks completed

        subtask = state["subtasks"][current_subtask_index]
        
        # Validate subtask structure
        if not isinstance(subtask, dict):
            raise ValueError(f"Invalid subtask format. Expected dict, got {type(subtask).__name__}: {subtask}")
        
        required_keys = ["subtask_description", "agent", "tools"]
        missing_keys = [key for key in required_keys if key not in subtask]
        if missing_keys:
            raise ValueError(f"Subtask missing required keys: {missing_keys}. Subtask: {subtask}")
        
        subtask_description = subtask["subtask_description"]
        agent_type = subtask["agent"]
        tools_to_use = subtask["tools"]

        # Prepare tools for the agent
        available_tools = {t.name: t for t in self.tools if t.name in tools_to_use}
        
        # Dynamically select agent role and prompt based on agent_type
        agent_system_message = "You are a helpful AI assistant."
        if agent_type == "summarizer":
            agent_system_message = "You are an expert summarizer. Condense information concisely."
        elif agent_type == "data_analyst":
            agent_system_message = "You are a skilled data analyst. Process data, identify trends, and generate code for analysis/visualization."
        elif agent_type == "researcher":
            agent_system_message = "You are a diligent researcher. Use web search to find relevant information."
        elif agent_type == "code_executor":
            agent_system_message = "You are a Python code execution expert. Execute provided code and return results."

        # Construct agent prompt with available tools
        tool_names = ", ".join(available_tools.keys())
        # Convert agent_results to JSON string and escape braces for ChatPromptTemplate
        import json
        agent_results_str = json.dumps(state['agent_results'], indent=2)
        # Escape curly braces for ChatPromptTemplate by doubling them
        agent_results_str = agent_results_str.replace('{', '{{').replace('}', '}}')
        
        agent_user_message = f"""Current subtask: {subtask_description}
        
        Here is the current context and previous results: {agent_results_str}

        You have access to the following tools: {tool_names}. Use them if necessary to complete your subtask.
        If you need to use a tool, respond with a JSON object in the format: {{{{"tool": "tool_name", "input": {{{{...}}}}}}}}
        Otherwise, provide your direct answer or the next step.
        """
        
        agent_response = await self._call_agent_llm_async(llm, agent_system_message, agent_user_message)
        
        # Check if the agent wants to use a tool
        try:
            response_json = json.loads(agent_response)
            if "tool" in response_json and "input" in response_json:
                tool_name = response_json["tool"]
                tool_input = response_json["input"]
                if tool_name in available_tools:
                    print(f"Agent {agent_type} using tool {tool_name} with input {tool_input}")
                    tool_result = await asyncio.to_thread(available_tools[tool_name].invoke, tool_input)
                    agent_response = f"Tool {tool_name} executed. Result: {tool_result}"
                else:
                    agent_response = f"Agent requested unknown or unavailable tool: {tool_name}"
        except json.JSONDecodeError:
            pass # Not a tool call, continue with direct response

        new_agent_results = state["agent_results"] + [{
            "subtask_description": subtask_description,
            "agent": agent_type,
            "result": agent_response
        }]
        
        return {"agent_results": new_agent_results, "current_subtask_index": current_subtask_index + 1}

    async def _aggregator_node(self, state: AgentState, config_dict: dict = None):
        llm = self.llm_manager.get_llm(state["llm_model_preference"])
        if not llm:
            raise ValueError("No LLM available for aggregation.")

        aggregator_prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are a final result aggregator. Combine all the subtask results into a coherent, structured, and comprehensive final answer for the user.
            The original user request was: {user_request}
            
            Subtask Results:
            {agent_results}
            
            Provide a clear and well-formatted final answer.
            """),
            ("user", "Original Request: {user_request}\nSubtask Results: {agent_results}")
        ])
        
        final_answer = await self._call_llm_async(llm, aggregator_prompt, state)
        return {"final_answer": final_answer}

    def _should_continue(self, state: AgentState):
        if state["current_subtask_index"] < len(state["subtasks"]):
            return "agent_executor"
        else:
            return "aggregator"

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("planner", self._planner_node)
        workflow.add_node("agent_executor", self._agent_executor_node)
        workflow.add_node("aggregator", self._aggregator_node)

        workflow.set_entry_point("planner")

        workflow.add_edge("planner", "agent_executor")
        workflow.add_conditional_edges(
            "agent_executor",
            self._should_continue,
            {
                "agent_executor": "agent_executor",
                "aggregator": "aggregator",
            },
        )
        workflow.add_edge("aggregator", END)

        return workflow.compile()

    async def execute_task(self, user_request: str, progress_callback=None, use_gpt4: bool = True, use_gemini: bool = False):
        print(f"\n>>> EXECUTE_TASK called with request: {user_request}", flush=True)
        print(f">>> LLM preference: use_gpt4={use_gpt4}, use_gemini={use_gemini}", flush=True)
        
        initial_state = AgentState(
            user_request=user_request,
            chat_history=[HumanMessage(content=user_request)],
            plan="",
            subtasks=[],
            current_subtask_index=0,
            agent_results=[],
            final_answer="",
            llm_model_preference='gpt4' if use_gpt4 else ('gemini' if use_gemini else self.llm_manager.available_models[0])
        )
        
        print(f">>> Initial state created, starting graph execution...", flush=True)
        
        # Stream events from the graph
        async for event in self.graph.astream(initial_state):
            print(f">>> Graph event received: {list(event.keys())}", flush=True)
            for key, value in event.items():
                if key != "__end__":
                    print(f"Node: {key}, Value: {value}", flush=True)
                    if progress_callback:
                        progress_callback(f"Node: {key} - {value.get('subtask_description', '')}")
            if "aggregator" in event:
                return event["aggregator"]["final_answer"]
        
        # Fallback if astream somehow finishes without aggregator event (shouldn't happen with END edge)
        print(f">>> Graph stream completed, using fallback ainvoke...", flush=True)
        final_state = await self.graph.ainvoke(initial_state)
        return final_state["final_answer"]
