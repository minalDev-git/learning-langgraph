# Implementing conditional logic in the overall graph structure
# Implement conditional logic to route the flow of data to different nodes.
# Use START and END nodes to manage entry and exit points explicitly.
# Create a router node to handle-decision making and control graph flow.

from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class AgentState(TypedDict):
    number1: int
    operation: str
    number2: int
    finalNumber: int

def adder(state:AgentState)-> AgentState:
    "This node adds 2 numbers"
    
    state['finalNumber'] = state['number1'] + state['number2']
    return state

def subtractor(state:AgentState)-> AgentState:
    "This node subtracts 2 numbers"

    state['finalNumber'] = state['number1'] - state['number2']
    return state

# Router node <-- this will be at the start of our graph (after start node). We'll let the router decide the operation (+ or -)
def decide_next_node(state:AgentState):
    """This node will select the next node of the graph"""

    if state['operation'] == '+':
        # we need to do a certain thing, to pass it to the next node. You don't actually call the "adder" func, instead you return the edge
        return "addition_operation"
    elif state['operation'] == '-':
        # we need to do a certain thing, to pass it to the next node. You don't actually call the "adder" func, instead you return the edge
        return "subtraction_operation"

graph = StateGraph(AgentState)

# This won't work. Reason: we are not returning the updated state in "decide_next_node"
# graph.add_node("router", decide_next_node)
# FIX: graph.add_node("router", lambda state: state) <- this means your input state will be your output exact same state
graph.add_node("add_node", adder)
graph.add_node("subtract_node", subtractor)
graph.add_node("router", lambda state: state) #passthrough function

graph.add_edge(START,"router")

# now making the conditional edges from your router to your operation nodes
graph.add_conditional_edges(
    "router", # source node name, from which the edges are branched out
    decide_next_node, #that's the path that tells what action source node ("router") needs to do
    # path map in form of dict
    {
        # Format: Edge: Node
        "addition_operation": "add_node",
        "subtraction_operation": "subtract_node"
    }
)

# We need 2 edges to connect to the END point.(one from add_node to )
graph.add_edge("add_node",END)
graph.add_edge("subtract_node",END)

app = graph.compile()

initial_state = AgentState(number1=10, operation='-',number2=5,finalNumber=0)
print(app.invoke(initial_state))