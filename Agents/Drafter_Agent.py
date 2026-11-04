# Mini Project: DRAFTER
# You are woking in a company and the boss comes to you. She has a problem and some orders for us.

# Problem: Our company is not working efficiently! We spend way too much time drafting documents and this needs to be fixed!
# For the company, you need to create an AI agentic system, that can speed up drafting documents, emails, etc. 
# The Agentic AI system should have an Human-AI collaboration, meaning the Human should be able to provide contionous feedback,
# and the AI Agent should stop when th Human is happy with thw draft. The system should also be fast and be able to save the drafts
import os
from typing import Annotated,Sequence,TypedDict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage,ToolMessage,SystemMessage, HumanMessage
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph,START,END
from langgraph.prebuilt import ToolNode

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# global variable to store document content
document_content = ""

class AgentState(TypedDict):
    messages : Annotated[Sequence[BaseMessage],add_messages]

@tool 
def update(content: str)->str: # the content param will be provided by the llm
    """Updates document with the provided content"""
    global document_content
    document_content = content

    return f"Document updated successfully! The current content is: \n{document_content}"

@tool
def save(filename: str)->str:
    # we request the llm to give a suitable filename for the text file.
    """Save the current document to a text file and finish the process.

    Args:
    filename: name of the text file.
    """
    global document_content
    # to make the drafter more robust
    if not filename.endswith(".txt"):
        filename = f"{filename}.txt"

    try:
        with open(filename,"w") as f:
            f.write(document_content)
            print(f"\nDocument has been saved to: {filename}")
            return f"Document has been saved sucessfully to: {filename}"
    except Exception as e:
        return f"Error saving the document: {str(e)}"

tools = [update, save]
model = ChatGroq(model="openai/gpt-oss-20b", temperature=0, api_key=GROQ_API_KEY).bind_tools(tools) # type: ignore

def our_agent(state: AgentState)->AgentState:
    # passing system message to our llm
    system_prompt = SystemMessage(content=f"""
    You are a Drafter, a helpful writing assistant. You are trying to help the user update and modify documents.

    - If the user wants to update or modify content, use the 'update' tool with the complete updated content.
    - If the user wants to save and finish, you need to use the 'save' tool.
    - Make sure to show the current document state after modifications.

    the current document content is {document_content}
    """)

    # when we are 1st initializing the graph, the 1st msg you'll be writing is: How are you going to change the document? b/c we haven't passed the doc yet.
    # if "messages" in AgentState is empty, we'll show an intro msg
    if not state["messages"]:
        user_input = "I'm ready to help you update a document. What would you like to create?"
        user_message = HumanMessage(content=user_input)

    # if we are in the process of updating the document
    else:
        user_input = input("\nWhat would you like to do with the document? ")
        print(f"\n USER: {user_input}")
        user_message = HumanMessage(content=user_input)
    
    all_messages = [system_prompt] + list(state["messages"]) + [user_message]
    response = model.invoke(all_messages)

    print(f"\n AI: {response.content}")
    if hasattr(response, "tool_calls") and response.tool_calls:
        tool_names = [tool_call["name"] for tool_call in response.tool_calls]
        print(f"USING TOOLS: {tool_names}")

    # returning the updated state
    return {"messages": list(state["messages"]) + [user_message, response]}

def should_continue(state:AgentState) -> str:
    """Determine if we should continue or end the conversation"""

    messages = state["messages"]
    if not messages:
        return "continue"

    # if we use the update tool, we obv need to use the "continue" edge but if we use "save" tool we'll use the "end" edge
    # This looks at the most recent tool message...
    for message in reversed(messages):
        # and checks if this is a ToolMessage resulting from save.
        if isinstance(message, ToolMessage):
            content = message.content
            text = content if isinstance(content, str) else str(content)
            lower_text = text.lower()
            if "saved" in lower_text and "document" in lower_text:
                return "end" # go to the end edge which leads to the endpoint.
    
    return "continue"

def print_messages(messages):
    """Function to print the messages in a more readable format"""
    if not messages:
        return

    # loops through the last 3 items of a list and extracts a sub-list containing only the final 3 elements.
    for message in messages[-3:]:
        if isinstance(message, ToolMessage):
            print(f"\n TOOL RESULT: {message.content}")

graph = StateGraph(AgentState)
graph.add_node("agent",our_agent)

tool_node = ToolNode(tools)
graph.add_node("tools", tool_node)

graph.add_edge(START,"agent")
graph.add_edge("agent","tools")
graph.add_conditional_edges(
    "tools",
    should_continue,
    {
        "continue": "agent",
        "end": END
    }
)

app = graph.compile()

# running the program
def run_document_agent():
    print("\n ======== DRAFTER ========")

    # we could've passed an already existing document string over here as well
    state = {"messages": []}

    for step in app.stream(state, stream_mode="values"): # type: ignore
        if "messages" in step:
            print_messages(step["messages"])

    print("\n ========= DRAFTER FINISHED =========")

if __name__ == "__main__":
    run_document_agent()
