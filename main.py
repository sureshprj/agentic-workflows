from pprint import pprint
from typing import TypedDict, Annotated

from langchain.schema import HumanMessage
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# Import your agents and tool nodes
from agents.planner import make_planner_agent
from agents.coder import make_coder_agent

# Instantiate planner and coder agents with their tool nodes
planner_agent, planner_tool_node = make_planner_agent()
coder_agent, coder_tool_node = make_coder_agent()

# Define the shared state structure
class State(TypedDict):
    messages: Annotated[list, add_messages]

# === Agent Nodes ===

def planner_agent_node(state: State) -> State:
    response = {"messages": [planner_agent.invoke(state["messages"])]}
    pprint(f"response from AI PLANNER: {response['messages'][-1]}")
    return response

def coder_agent_node(state: State) -> State:
    response = {"messages": [coder_agent.invoke(state["messages"])]}
    pprint(f"response from AI CODER: {response['messages'][-1]}")
    return response

# === Conditional Routing Logic ===

def planner_condition(output: dict) -> dict:
    if "tool_calls" in output["messages"][-1].__dict__:
        return {"planner_tool_node": True}
    return {"coder_agent_node": True}  # Transition to coder if planner is done

def coder_condition(output: dict) -> dict:
    if "tool_calls" in output["messages"][-1].__dict__:
        return {"coder_tool_node": True}
    return {"END": True}  # End flow if coding is done

# === Graph Setup ===

memory = MemorySaver()
builder = StateGraph(State)

# Add all nodes
builder.add_node("planner_agent_node", planner_agent_node)
builder.add_node("planner_tool_node", planner_tool_node)
builder.add_node("coder_agent_node", coder_agent_node)
builder.add_node("coder_tool_node", coder_tool_node)

# Edges must follow this correct order
builder.add_edge(START, "planner_agent_node")

# ✅ Add CONDITIONAL EDGES before any add_edge for same node
builder.add_conditional_edges("planner_agent_node", planner_condition)
builder.add_edge("planner_tool_node", "planner_agent_node")  # OK

builder.add_conditional_edges("coder_agent_node", coder_condition)
builder.add_edge("coder_tool_node", "coder_agent_node")  # OK

# Compile the graph
graph = builder.compile(checkpointer=memory)

# === Optional: Graph Image for Debugging (Jupyter) ===

def show_graph_image():
    from IPython.display import Image, display
    display(Image(graph.get_graph().draw_mermaid_png()))

# === Main Chat Loop ===

def run_chat():
    print("Code Gen (type 'exit' to quit)")
    config = {'configurable': {'thread_id': 133}}
    while True:
        user_input = input("You: ")
        if user_input.lower() in {"quit", "exit"}:
            break

        response = graph.invoke({
            "messages": [HumanMessage(content=user_input)]
        }, config)  # Safety limit to avoid infinite loops

        print(f"AI: {response['messages'][-1].content}")

# === Entry Point ===

if __name__ == "__main__":
    run_chat()
