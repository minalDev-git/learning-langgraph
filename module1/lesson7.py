# Agent with memory

import os
from pprint import pprint
from dotenv import load_dotenv
from langchain_groq import ChatGroq

from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode,tools_condition
from langchain_core.messages import HumanMessage,SystemMessage
from langgraph.graph import MessagesState
from langgraph.graph import StateGraph,START

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0, api_key=GROQ_API_KEY) # type: ignore

@tool
def multiply (a:int, b:int) ->int:
    """Multiply a and b

    Args:
        a: first int
        b: second int
    """
    return a * b
@tool
def add (a:int, b:int) ->int:
    """Adds a and b

    Args:
        a: first int
        b: second int
    """
    return a + b
@tool
def divide (a:int, b:int) ->float:
    """Divides a by b

    Args:
        a: first int (numerator)
        b: second int (denominator)
    """
    return a / b

tools = [multiply, add, divide]
llm_with_tools = llm.bind_tools(tools)

system_prompt = SystemMessage(content="""You are a helpful assistant tasked with performing airthmetic on a set of inputs.""")

# Assistant Node
def assistant(state:MessagesState)-> MessagesState:
    return {"messages":[llm_with_tools.invoke([system_prompt] + state["messages"])]}

builder = StateGraph(MessagesState)
builder.add_node("assistant",assistant)
builder.add_node("tools", ToolNode(tools))

builder.add_conditional_edges(
    "assistant",
    tools_condition
)
builder.add_edge(START,"assistant")
builder.add_edge("tools","assistant")

graph = builder.compile()

# one graph execution, which has some state, resulting in "7"
messages = [HumanMessage(content="Add 3 and 4")]
messages = graph.invoke({"messages":messages}) # type: ignore

for m in messages['messages']:
    m.pretty_print()

# Second independant graph execution, which has new state, and has no persistence b/w the prev execution and this one
messages = [HumanMessage(content="Multiply that by 2")]
messages = graph.invoke({"messages":messages}) # type: ignore

for m in messages['messages']:
    m.pretty_print()

from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()
react_graph_memory = builder.compile(checkpointer=memory)

# Implementing Memory:

# specify a thread
config = {"configurable": {"thread_id": "1"}}

# specify an input
messages = [HumanMessage(content="Add 3 and 4")]

# Run
messages = react_graph_memory.invoke({"messages": messages}, config) # type: ignore
# for m in messages['messages']:
#     m.pretty_print()

# pass the same thread_id (using the config) to proceed from the previously logged checkpoint
messages = [HumanMessage(content="Multiply that by 2")]
messages = react_graph_memory.invoke({"messages": messages}, config) # type: ignore
for m in messages['messages']:
    m.pretty_print() # Now this prints the entire state: prev + new

# When I compile my graph for LangSmith Studio, I don't actually need to supply checkpointer. <--Reason:
# Studio is backed by the LangGraph API. The API takes its code and packages it for you, and it has its own persistence layer
# so it's all done for you