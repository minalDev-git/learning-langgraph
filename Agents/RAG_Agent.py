import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from typing import Annotated,Sequence,TypedDict
from langchain_core.messages import BaseMessage,ToolMessage,AIMessage,HumanMessage,SystemMessage
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.tools import tool

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
pdf_path= os.path.join(os.path.dirname(__file__), "Stock_Market_Performance_2024.pdf")
PERSIST_DIR = "./chroma_db"
collection_name = "stock_market"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0, api_key=GROQ_API_KEY) # type: ignore

if not os.path.exists(pdf_path):
    raise FileNotFoundError (f"PDF file not Found: {pdf_path}")

# loading the pdf
pdf_loader = PyPDFLoader(pdf_path)

# Chunking Strategy
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000,
    chunk_overlap = 200,
    separators=["\n\n", "\n", ". ", " ", ""],
)

def ingestion(docs):
    try:
        # creating the vectorstore and storing the chunks
        vectorstore = Chroma.from_documents(
            documents=docs,
            embedding=embedding_model,
            persist_directory=PERSIST_DIR,
            collection_name=collection_name
        )
        print(f"Created Chroma DB vectorstore")
        return vectorstore
    except Exception as e:
        print(f"Error setting Chroma: {str(e)}")
        raise

# checks if the pdf loads correctly
try:
    pages = pdf_loader.load()
    print(f"PDF has been loaded and has {len(pages)} pages")
    pages_split = text_splitter.split_documents(pages)

    # if the collection doesn't exist in the directory, create it using the os command
    if not os.path.exists(PERSIST_DIR):
        os.makedirs(PERSIST_DIR)

    vectorstore = ingestion(pages_split)

    if not vectorstore == None:
        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k":5} # Top-k chunks will be returned
        )

except Exception as e:
    print(f"Error loading PDF: {e}")

@tool
def retriever_tool(query: str)-> str:
    """
    This tool searches and returns the information from the Stock Market Performance 2024 document.
    """

    docs = retriever.invoke(query)

    if not docs:
        return "I find no relevant information in the Stock Market Performance 2024 document."

    results = []
    for i, doc in enumerate(docs):
        results.append(f"Document {i+1}: \n{doc.page_content}")
    return "\n\n".join(results)

tools = [retriever_tool]

llm = llm.bind_tools(tools)

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


# underlying function behind conditional edge
def should_continue(state:AgentState):
    """Checks if the last message contains tool calls"""
    # if it does then we'll proceed, otherwise we'll end
    result = state["messages"][-1]
    return hasattr(result,"tool_calls") and len(result.tool_calls) > 0 # type: ignore

system_prompt = """
You are an intelligent AI assistant who answers questions about Stock Market Performance in 2024 based on the PDF document loaded into your knowledge base.
Use the retriever tool available to answer questions about the stock market performance data. You can make multiple calls if needed.
If you need to look up some information before asking a follow up question, you are allowed to do that!
Please always cite the specific parts of the documents you use in your answers.
"""

tools_dict = {our_tool.name: our_tool for our_tool in tools}

# LLM Agent
def call_llm(state:AgentState)->AgentState:
    """Node to call the LLM with the current state."""
    messages = list(state["messages"])

    # pass the system prompt
    messages = [SystemMessage(content=system_prompt)] + messages
    message = llm.invoke(messages)

    return {"messages": [message]}

# Retriever Agent 
#  deciding whether the tool decided by the llm is valid or not. If it is valid, it will invoke the tool and store the results
def take_action(state: AgentState) -> AgentState:
    """Execute tool calls from LLM's response."""

    # if the tool name is the proper specified tool (aka retriever_tool), then run it. If it's not, then show the error
    tool_calls = state["messages"][-1].tool_calls # type: ignore
    results = []

    for t in tool_calls:
        print(f"Calling Tools: {t["name"]} with query {t["args"].get("query", "No query provided")}")

        if not t["name"] in tools_dict: # Checks if a valid tool is present
            print(f"\nTool: {t["name"]} does not exist")
            result = "Incorrect Tool Name. Please Retry and Select tool from list of Available tools."

        else:
            result = tools_dict[t["name"]].invoke(t["args"].get("query", ""))
            print(f"Result Length: {len(str(result))}")

        # Appends the Tool Message in the results
        results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))

    print("Tool Execution Completed, Back to model!")

    return {"messages": results}

# Creating the graph
graph = StateGraph(AgentState)
graph.add_node("llm", call_llm)
graph.add_node("retriever_agent", take_action)

graph.add_conditional_edges(
    "llm",
    should_continue, # <--this function return True or False
    {
        True: "retriever_agent",
        False: END
    }
)

graph.add_edge(START,"llm")
graph.add_edge("retriever_agent","llm")

rag_agent = graph.compile()

# allows us to keep asking questions from the RAG agent until user enters "exit" or "quit"
def running_agent():
    print("\n=== RAG AGENT===")
    
    while True:
        user_input = input("\nWhat is your question: ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        messages = [HumanMessage(content=user_input)] # converts back to a HumanMessage type

        result = rag_agent.invoke({"messages": messages})
        
        print("\n=== ANSWER ===")
        print(result['messages'][-1].content)

running_agent()