"""
AI Code Generator Agent

A multi-agent system that generates complete projects from natural language prompts.
Uses LangGraph for workflow orchestration and Groq LLM for intelligent code generation.

Three specialized agents work in sequence:
1. Planner Agent: Converts user prompts into structured project plans
2. Architect Agent: Breaks down plans into implementation tasks
3. Coder Agent: Implements tasks iteratively with file operations
"""

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent

from prompts import planner_prompt, architect_prompt, coder_system_prompt
from states import Plan, TaskPlan, CoderState
from tools import write_file, read_file, get_current_directory, list_files

# Load environment variables from .env file
load_dotenv()

# Initialize LLM with Groq
llm = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct")


# ==================== AGENT FUNCTIONS ====================

def planner_agent(state: dict) -> dict:
    """
    Planner Agent: Converts user prompt into a comprehensive engineering project plan.
    
    Generates:
    - Project name and description
    - Tech stack selection
    - Feature list
    - File structure with purposes
    
    Args:
        state: Dict containing 'user_prompt' key
        
    Returns:
        Dict with 'plan' key containing structured Plan object
    """
    user_prompt = state["user_prompt"]
    resp = llm.with_structured_output(Plan).invoke(planner_prompt(user_prompt))
    
    if resp is None:
        raise ValueError("Planner did not generate a valid response")
    
    return {"plan": resp}


def architect_agent(state: dict) -> dict:
    """
    Architect Agent: Breaks down project plan into explicit implementation tasks.
    
    Creates:
    - Implementation tasks for each file
    - Task descriptions with specific requirements
    - Dependency ordering (dependencies implemented first)
    - Integration context and function signatures
    
    Args:
        state: Dict containing 'plan' key
        
    Returns:
        Dict with 'task_plan' key containing structured TaskPlan object
    """
    plan: Plan = state["plan"]
    resp = llm.with_structured_output(TaskPlan).invoke(architect_prompt(plan))
    
    if resp is None:
        raise ValueError("Architect did not generate a valid response")
    
    # Attach original plan for reference
    resp.plan = plan
    return {"task_plan": resp}


def coder_agent(state: dict) -> dict:
    """
    Coder Agent: Implements tasks iteratively using ReAct pattern.
    
    For each task:
    - Reads existing file content for context
    - Uses LLM with file operation tools to write code
    - Maintains consistency across modules
    - Advances to next task
    
    Loops until all implementation tasks are complete.
    
    Args:
        state: Dict containing 'task_plan' and optionally 'coder_state'
        
    Returns:
        Dict with updated 'coder_state' and optional 'status' completion flag
    """
    
    # Initialize or retrieve coder state
    coder_state: CoderState = state.get("coder_state")
    if coder_state is None:
        coder_state = CoderState(
            task_plan=state["task_plan"], 
            current_step_idx=0
        )
    
    # Check if all tasks are complete
    steps = coder_state.task_plan.implementation_steps
    if coder_state.current_step_idx >= len(steps):
        return {"coder_state": coder_state, "status": "DONE"}
    
    # Get current task
    current_task = steps[coder_state.current_step_idx]
    
    # Read existing file content for context
    existing_content = read_file.run(current_task.filepath)
    
    # Build context-aware prompt for the coder
    user_prompt = (
        f"Task: {current_task.task_description}\n"
        f"File: {current_task.filepath}\n"
        f"Existing content:\n{existing_content}\n"
        "Use write_file(path, content) to save your changes."
    )
    
    system_prompt = coder_system_prompt()
    
    # Create ReAct agent with file operation tools
    coder_tools = [read_file, write_file, list_files, get_current_directory]
    react_agent = create_react_agent(llm, coder_tools)
    
    # Execute agent to implement the task
    react_agent.invoke({
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    })
    
    # Advance to next task
    coder_state.current_step_idx += 1
    return {"coder_state": coder_state}


# ==================== GRAPH CONSTRUCTION ====================

def build_agent_graph():
    """
    Constructs the LangGraph workflow with three agents in sequence.
    
    Flow:
    planner → architect → coder (loops until done) → END
    
    Returns:
        Compiled graph ready for execution
    """
    graph = StateGraph(dict)
    
    # Add agent nodes
    graph.add_node("planner", planner_agent)
    graph.add_node("architect", architect_agent)
    graph.add_node("coder", coder_agent)
    
    # Define sequential edges
    graph.add_edge(start_key="planner", end_key="architect")
    graph.add_edge(start_key="architect", end_key="coder")
    
    # Conditional edge: coder loops until all tasks complete
    graph.add_conditional_edges(
        "coder",
        lambda s: "END" if s.get("status") == "DONE" else "coder",
        {"END": END, "coder": "coder"}
    )
    
    # Set entry point
    graph.set_entry_point("planner")
    
    return graph.compile()


# Compile the agent graph
agent = build_agent_graph()


# ==================== ENTRY POINT ====================

if __name__ == "__main__":
    # Example usage
    user_prompt = "Create a simple calculator web application"
    
    print("\n" + "="*70)
    print("🤖 AI CODE GENERATOR - Multi-Agent Code Generation System")
    print("="*70)
    print(f"\n📝 Generating code for: {user_prompt}\n")
    
    # Execute the agent graph
    result = agent.invoke({"user_prompt": user_prompt})
    
    print("\n" + "="*70)
    print("✅ Code generation complete!")
    print("📁 Generated files are in: generated_project/")
    print("="*70 + "\n")
