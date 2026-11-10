# ReAct agent (a general agent architecture):
# 1. act --> let the model call specific tools
# 2. observe --> pass the tool output back to the model
# 3. reason --> let the model reason about the tool output, to decide what to do next (e.g call anotger tool or respond directly)
# 4. loop continues as long as the model continues calling tools unless you add a max recursion limit

from langgraph.graph import StateGraph,START, END
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode # node used to call our tools, simply pass a list of tools to initialize it
from langgraph.prebuilt import tools_condition # Conditional routing function for tool-calling workflows
from langchain_core.messages import HumanMessage,SystemMessage
from langgraph.graph import MessagesState

import os
from pprint import pprint
from dotenv import load_dotenv
from langchain_groq import ChatGroq

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

# Node
def assistant(state: MessagesState):
    msgs = llm_with_tools.invoke([system_prompt]+ state["messages"])
    return {"messages": [msgs]}

tool_node = ToolNode(tools)

builder = StateGraph(MessagesState)
builder.add_node("assistant",assistant)
builder.add_node("tools",tool_node)

builder.add_edge(START,"assistant")
builder.add_conditional_edges(
    "assistant",
    tools_condition
)
builder.add_edge("tools","assistant")
graph = builder.compile()


msgs = [HumanMessage(content="Add 3 and 4. Multiply the output by 2. Divide the output by 5.")]
msgs = graph.invoke({"messages": msgs}) # type: ignore

for m in msgs["messages"]:
    m.pretty_print()

# looking at the trace on LangSmith:
# b/c I set the env variable My Project Name,It creates this project, which logs traces with it logged traces associated with this project too.
os.environ["LANGCHAIN_PROJECT"] = "langchain_academy"  # type: ignore