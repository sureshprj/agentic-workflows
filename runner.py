# chatbot_tool_graph.py

import os
from dotenv import load_dotenv
from pprint import pprint
from typing import TypedDict, Annotated

from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
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

#llm = ChatOpenAI(model_name="gpt-4-turbo")
llm = ChatAnthropic(model_name="claude-opus-4-20250514")
prompt = ChatPromptTemplate.from_messages([
    ("system", """
Your sole responsibility is to generate a clear, structured development plan for an e-commerce project based on user input. Another agent will use this plan in the next step to implement the actual code, so ensure each step is precise, actionable, and well-organized.

### Goal:
Create a development plan for an e-commerce website and save it to the `e-commerce-01/plans.md` file.

You must **immediately use your available tools** to write the plan into the `plans.md` file within the `e-commerce-01/` directory.


### Instructions:
- Refer to the sample plan located at `sample/sample_plan.md` for formatting, structure, and tone.
- If `plans.md` already exists, **append to or update** it as needed.
- Do **not** respond to the user in plain text.
- After saving the plan, return a **brief summary** of what was written, then stop all further actions (including tool use).
- Do **not** initiate or create any development-related files or tasks.
- Assume the entire development process will be fully automated by AI agents. Avoid unnecessary details such as timelines, resources, or team roles.
- make multiple tools call if require, 
### Output:
Return a short summary of the content added to `plans.md`.


"""),
    ("human", "{input}")
])
planning_agent_runnable = prompt | llm.bind_tools(file_tool_list)

# === 4. GRAPH STATE AND NODES ===

class State(TypedDict):
    messages: Annotated[list, add_messages]

def agent_node(state: State) -> State:
    """Chat node that invokes the LLM with tool support."""
   
    response = {"messages": [planning_agent_runnable.invoke(state["messages"])]}
    pprint(f"response from AI: {response['messages'][-1]}")
    return response


# === 5. BUILD GRAPH ===

memory = MemorySaver()
builder = StateGraph(State)

builder.add_node("agent_node", agent_node)
builder.add_node("tools", ToolNode(file_tool_list))

builder.add_edge(START, "agent_node")
builder.add_conditional_edges("agent_node", tools_condition)
builder.add_edge("tools", "agent_node")
#builder.add_edge("agent_node", END)

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
            "messages": [HumanMessage(content=user_input)]
        }, config)
        print(f"after responsee {response['messages'][-1].content}")


if __name__ == "__main__":
    print("Chatbot with Tool-Enhanced LLM (type 'exit' to quit)")
    run_chat()
