# create multiple nodes that sequentially process and update different parts of the state
#  connect nodes together in a graph

from langgraph.graph import StateGraph
from typing import TypedDict

class AgentState(TypedDict):
    name: str
    age: str
    final: str

def first_node(state:AgentState)->AgentState:
    """This is the first node of our sequence"""

    state['final'] = f"Hi {state['name']}."
    return state

def second_node(state:AgentState)->AgentState:
    """This is the second node of our sequence"""

    # state['final'] = f"You are {state['age']} years old" <-- logical error, bcuz we completely replaced the state['final'] val from first node
    state['final'] = state['final'] + f" You are {state['age']} years old" #by doing this the error should be solved
    return state

graph = StateGraph(AgentState)

graph.add_node("first_node", first_node)
graph.add_node("second_node", second_node)

graph.set_entry_point("first_node")
# Connecting the first_node and second_node using an edge(directed edge)
graph.add_edge("first_node","second_node")
graph.set_finish_point("second_node")

app = graph.compile()
result = app.invoke({"name":"Bob","age":"32","final":""})
print(result["final"])