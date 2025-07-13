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

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.environ.get("OPEN_API_KEY")

def make_agent(prompt: str, tools: list):
    llm = ChatOpenAI(model_name="gpt-4-turbo")
    #llm = ChatAnthropic(model_name="claude-opus-4-20250514")
    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", prompt),
        ("human", "{input}")
    ])

    agent = chat_prompt | llm.bind_tools(tools)
    return agent