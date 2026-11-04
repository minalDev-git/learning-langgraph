# ReAct Agent: START -> Agent -> END Loop: b/w Agent and Tools
# We give agent access to tools and its the agent's job to be able to decide which tool to select and when tool calling is no longer neededs
# Objectives: 
# 1. Learn Tools in LangGraph
# 2. How to create a ReAct Graph
# 3. Work with different types of Messages such as ToolMessages
# 4. Test out robustness of the graph
import os
from typing import Annotated, TypedDict, Sequence
from dotenv import load_dotenv

load_dotenv()
from langchain_core.messages import BaseMessage # The foundational class for all message types in langGraph
from langchain_core.messages import ToolMessage # Passes data back to llm after it calls a tool such as the content and the tool_call_id
from langchain_core.messages import SystemMessage # Message for providing instructions to the llm
from langchain_core.messages import HumanMessage # Message for user input
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START,END
from langgraph.prebuilt import ToolNode

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
class AgentState(TypedDict):
    # preserve the state by actually appending it rather than overwriting it.
    # Sequence[BaseMessage] describes the type of the state value.
    # add_messages tells LangGraph how to update that state field.
    messages: Annotated[Sequence[BaseMessage], add_messages]

# Creating the first tool
@tool
def add(a:int, b:int)->int:
    """This is an addition function that adds 2 numbers together"""

    return a + b
@tool
def subtract (a:int, b:int)->int:
    """This is an subtraction function that subtracts 2 numbers together"""

    return a - b
@tool
def multiply(a:int, b:int)->int:
    """This is an multiplication function that multiplies 2 numbers together"""

    return a * b

tools = [add,subtract,multiply]
# Giving the llm the list of tools
model = ChatGroq(model="openai/gpt-oss-20b", temperature=0, api_key=GROQ_API_KEY).bind_tools(tools) # type: ignore

# Create a node that accesses the agent within our Graph. 
def model_call(state: AgentState)->AgentState:
    system_prompt = SystemMessage(content= "you are a helpful AI assistant. Answer my query to the best of your ability. keep your answers short.")
    
    # We need to pass the user query so that the llm respond to it. we do it by adding state["messages"]
    response = model.invoke([system_prompt] + list(state["messages"]))

    # method of writing updated state b/c the reducer func "add_messages handles the updating for us. It doesn't overwrite the msgs"
    return {"messages":[response]}

# Adding a conditional edge which decides that the llm should call the tools or not.
def should_continue(state: AgentState):
    # Essentially when we pass our query to the llm, we'll create a list of tools. Evey msg will tell if it requires tool_calling
    # we will see the last msg and check if there's anymore tools needed to be ran.

    messages = state["messages"]
    last_message = messages[-1]

    if not last_message.tool_calls: # type: ignore
        return "end" #no more tool_calling needed

    else:
        return "continue" # going to the tool node

# creating the graph
graph = StateGraph(AgentState)
graph.add_node("our_agent", model_call)
graph.add_edge(START,"our_agent")

# creating the ToolNode
tool_node = ToolNode(tools=tools)
graph.add_node("tools",tool_node)

# conditional edge only provides a one-way directed edge from either Agent-->tool node or Agent-->End node
graph.add_conditional_edges(
    "our_agent",
    should_continue,
    {
        "continue": "tools",
        "end": END,
    }
)

# adding an edge that goes back from tool node to our agent Tools --> Agent
graph.add_edge("tools","our_agent")
app = graph.compile()

# output the tool calling in a much better way
def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message,tuple):
            print(message)
        else:
            message.pretty_print()

# we prompt the llm so it uses multiple tools together, and also responds to queries that don't require tool calling
inputs = {"messages": [HumanMessage(content="Add 40 + 12 and then multiply by 6. Also tell me a joke please")]}
print_stream(app.stream(inputs,stream_mode="values")) # type: ignore