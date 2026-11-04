# Router: ChatModel routes b/w a direct response of tool call based on user's input
# Add a node that'll actually call our tool <-- execute tool_call in a node
# Add a conditional edge that will look at the ChatModel output, and route to our tool calling node or simply end if no tool calling is performed

from langgraph.graph import StateGraph,START, END
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode # node used to call our tools, simply pass a list of tools to initialize it
from langgraph.prebuilt import tools_condition # Conditional routing function for tool-calling workflows
from langchain_core.messages import HumanMessage

import os
from pprint import pprint
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0, api_key=GROQ_API_KEY) # type: ignore

@tool
def multiply(a:int, b:int) ->int:
    """Multiply a and b

    Args:
        a: first int
        b: second int
    """
    return a * b

llm_with_tools = llm.bind_tools([multiply])
# tool_call = llm_with_tools.invoke([HumanMessage(content=f"What is 2 multiplied by 3?", name="Minal")])

from langgraph.graph import MessagesState
class State(MessagesState):
    # add any keys beyond messages, which is pre-built
    pass

# Node
def tool_calling_llm(state: MessagesState) -> MessagesState:
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# Build graph
builder = StateGraph(MessagesState)
builder.add_node("tool_calling_llm",tool_calling_llm)
builder.add_node("tools", ToolNode([multiply])) # ToolNode is instantiated with this tool

builder.add_edge(START,"tool_calling_llm")
builder.add_conditional_edges(
    "tool_calling_llm",
    # If the latest msg (result) from assistant is a tool call -> "tools_condition" routes to tools
    # If the latest msg (result) from assistant is not a tool call -> "tools_condition" routes to END
    tools_condition, # <- handles the routing automatically
)
builder.add_edge("tools",END)
graph = builder.compile()

msgs = graph.invoke({"messages": [HumanMessage(content="Multiply 2 and 3!")]})
msgs = graph.invoke({"messages": [HumanMessage(content="Hello world!")]})

for m in msgs["messages"]:
    m.pretty_print()