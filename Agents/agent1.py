#  Simple Q & A bot (without memory)
# Ojective: how to integrate llms in our graphs
from dotenv import load_dotenv
from typing import TypedDict, List
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END

load_dotenv()

class AgentState(TypedDict):
    messages: List[HumanMessage] #list of human msgs provided by the user

llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0)

def process(state:AgentState)->AgentState:
    # calling the llm
    response = llm.invoke(state["messages"]) #we pass the human msgs to the llm (prompting the llm)

    print(f"\nAI: {response.content}")
    return state

graph = StateGraph(AgentState)
graph.add_node("process", process)
graph.add_edge(START,"process")
graph.add_edge("process",END)
agent = graph.compile()

# invoking the llm until user types "exit"
print("Enter your prompt. type 'exit' to stop")
user_input = input("Enter: ")
while user_input != "exit":
    agent.invoke({"messages":[HumanMessage(content=user_input)]})
    user_input = input("Enter: ")