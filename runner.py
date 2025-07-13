# chatbot_tool_graph.py

import os
from dotenv import load_dotenv
from pprint import pprint
from typing import TypedDict, Annotated

from langchain.schema import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition, create_react_agent
from langgraph.checkpoint.memory import MemorySaver

#tools import 
from tools.file_tools import file_tool_list

# === 1. ENVIRONMENT SETUP ===

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.environ.get("OPEN_API_KEY")


# === 2. LLM SETUP ===

llm = ChatOpenAI(model_name="gpt-3.5-turbo")


# === 3. Agent Creation ===
prompt = """
Act as a Project Manager.
Our objective is to build an HTML page along with the corresponding JavaScript functionality, based on user input.
The project will be structured under the path: 'e-commerce-01`.

Your task:

Define a clear and actionable implementation plan in a file named plans.md.

The plan should guide the development of the HTML and JavaScript files required to fulfill future user requests.

Assume the user will request various types of e-commerce pages (e.g., product listing, cart page, product detail, checkout, etc.).

Please outline a reusable structure and a flexible development workflow in plans.md to accommodate the different types of e-commerce pages users might request.
"""
planning_agent_runnable = create_react_agent(
    llm,
    file_tool_list,
    prompt=prompt
)


# === 4. GRAPH STATE AND NODES ===

class State(TypedDict):
    messages: Annotated[list, add_messages]


def agent_node(state: State) -> State:
    """Chat node that invokes the LLM with tool support."""
    print(f"before node_invoke {state}")
    response = {"messages": [planning_agent_runnable.invoke(state["messages"])]}
    print(f"after node_invoke {response}")
    return response


# === 5. BUILD GRAPH ===

memory = MemorySaver()
builder = StateGraph(State)

builder.add_node("agent_node", agent_node)
builder.add_node("tools", ToolNode(file_tool_list))
builder.add_edge(START, "agent_node")
builder.add_conditional_edges("agent_node", tools_condition)
builder.add_edge("tools", "agent_node")
builder.add_edge("agent_node", END)
graph = builder.compile(checkpointer=memory)


# === 6. OPTIONAL: DISPLAY GRAPH (only works in notebooks) ===
def show_graph_image():
    """Displays the compiled graph image (only works in notebooks)."""
    from IPython.display import Image, display
    display(Image(graph.get_graph().draw_mermaid_png()))


# === 7. MAIN CHAT LOOP ===

def run_chat():
    """Runs the chatbot in an interactive loop."""
    config = {'configurable': {'thread_id': 133}}

    while True:
        user_input = input("You: ")
        if user_input.lower() in {"quit", "exit"}:
            break

        response = graph.invoke({
            "messages": HumanMessage(content=user_input)
        }, config)

        chat_history = response["messages"]
        pprint(chat_history)


if __name__ == "__main__":
    print("Chatbot with Tool-Enhanced LLM (type 'exit' to quit)")
    run_chat()
