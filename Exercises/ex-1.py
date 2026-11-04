from langgraph.graph import StateGraph
from typing import TypedDict

class AgentState(TypedDict):
    message: str

def compliment_node(state:AgentState)->AgentState:
    """A simple node that adds a complementing message to the state"""

    state['message'] = f"{state['message']}, you're doing an amazing job learning LangGraph!"

    return state

graph = StateGraph(AgentState)

graph.add_node("complimenter", compliment_node)
graph.set_entry_point("complimenter")
graph.set_finish_point("complimenter")

app = graph.compile()
result = app.invoke({"message":"Bob"})
print(result["message"])