# Chains
from pprint import pprint
from langgraph.graph import StateGraph,START, END
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage, AnyMessage

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

# Messages: define a ChatModel, pass a list of msgs, get an AI msg back out with some content and metadata
messages: list[BaseMessage] = [AIMessage(content=f"So you said you were researching ocean mamals?", name="Model")]
messages.extend([HumanMessage(content=f"Yes, that's right.", name="Minal")])
messages: list[BaseMessage] = [AIMessage(content=f"Great, What would you like to learn about?", name="Model")]
messages.extend([HumanMessage(content=f"I want to learn about the best place to see Orcas in the US", name="Minal")])

for m in messages:
    m.pretty_print()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0, api_key=GROQ_API_KEY) # type: ignore

# result = llm.invoke(messages)
# print(type(result), result.response_metadata)

# Tools: needed whenever you want a model to control parts of your code or call out to external APIs
# Python fuction: ChatModel.bind_tools(<list of tools>) <-- Binding tools to ChatModels

@tool
def multiply(a:int, b:int) ->int:
    """Multiply a and b

    Args:
        a: first int
        b: second int
    """
    return a * b

llm_with_tools = llm.bind_tools([multiply])
tool_call = llm_with_tools.invoke([HumanMessage(content=f"What is 2 multiplied by 3?", name="Minal")])
# print(tool_call,"\n",tool_call.additional_kwargs['tool_calls'])

# Using messages as graph state
# class AgentState(TypedDict):
    # To preserve a full history of the conversation, we use reducer function
    # when we define our state in langgraph, we can annotate "messages" with the reducer function. This tells langgraph
    # to append to this messages list when it recieves a new msg
    # messages: Annotated[List[AnyMessage], add_messages]

# Alternatively you could implement the above thing like this too:
from langgraph.graph import MessagesState
class State(MessagesState):
    # add any keys beyond messages, which is pre-built
    pass

# Node
def tool_calling_llm(state: MessagesState) -> MessagesState:
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

#  Build graph
builder = StateGraph(MessagesState)

builder.add_node("tool_calling_llm",tool_calling_llm)

# Logic
builder.add_edge(START,"tool_calling_llm")
builder.add_edge("tool_calling_llm",END)

graph = builder.compile()
msgs = graph.invoke({"messages": [HumanMessage(content="Hello!")]})
print(msgs)
msgs = graph.invoke({"messages": [HumanMessage(content="Multiply 2 and 3!")]})
print(msgs)