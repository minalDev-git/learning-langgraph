# A conversational Chatbot 
# Objective: Create a form of memory for our Agent

from dotenv import load_dotenv
from typing import TypedDict, List, Union
from langchain_core.messages import HumanMessage, AIMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END

load_dotenv()

class AgentState(TypedDict):
    messages: List[Union[HumanMessage,AIMessage]] # any one of these data types are allowed & other than these are not allowed

llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0)

def process(state: AgentState)->AgentState:
    """This node will solve the request you input"""

    response = llm.invoke(state["messages"])
    state["messages"].append(AIMessage(response.content))
    # print(f"\nAI: {response.content}")
    print(f"CURRENT STATE: {state['messages']}")
    
    return state

graph = StateGraph(AgentState)
graph.add_node("process", process)
graph.add_edge(START,"process")
graph.add_edge("process",END)
agent = graph.compile()

# Maintainig the conversation history <- basically a short-term memory
conversation_history = []
user_input = input("Enter: ")
while user_input != "exit":
    conversation_history.append(HumanMessage(content=user_input))
    # the entire conversation history is sent to llm
    result = agent.invoke({"messages": conversation_history})

    print(result["messages"])
    # set conversation_history as the updated history after each Human-AI pair msgs
    # 
    conversation_history = result["messages"]

    user_input = input("Enter: ")

# Saving the history in a text file
with open('logging.txt',"w") as f:
    f.write("Your Conversation log")
    for message in conversation_history:
        if isinstance(message, HumanMessage):
            f.write(f"You: {message.content}\n")
        if isinstance(message, AIMessage):
            f.write(f"AI: {message.content}\n\n")

    f.write("End of Conversation")

print("Conversation saved to logging.txt")