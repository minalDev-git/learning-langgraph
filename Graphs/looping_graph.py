# Implement looping logic to route the flow of data back to the nodes.
# Create single conditional edge to handle decision making and control graph flow.
# we could've used a for-loop but for understanding purposes we are using the graph's looping logic

from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END
import random

class AgentState(TypedDict):
    name: str
    numbers: List[int]
    counter: int # to know when to stop the loop

def greeting_node(state: AgentState) -> AgentState: 
    """Greeting node which says hi to the person"""

    state['name'] = f"Hi there, {state['name']}"
    # initializing the counter over here b/c it vipes out if the user inputs a rubbish value e.g -2 in which case we would get 7 numbers
    state['counter'] = 0

    return state

def random_node(state: AgentState) -> AgentState:
    """This node generates a random number from 0 to 10"""

    # appending the randomly generated number in the numbers list
    state['numbers'].append(random.randint(0,10))

    # incrementing the counter value
    state['counter'] += 1

    return state

# Looping Logic: Since the client doesn't want any other node, we won't add the router node
# So we'll start by creating a conditional-edge.

def should_continue(state: AgentState):
    """Function to decide what to next"""

    # looping logic
    if state['counter'] < 5:
        print("ENTERING_LOOP", state['counter'])
        return "loop" # Continue looping
    else:
        return "exit" # Exit the loop

# greeting -> random -> random -> random -> random -> random -> END

graph = StateGraph(AgentState)

graph.add_node("greeting", greeting_node)
graph.add_node("random", random_node)

graph.add_edge("greeting", "random")
graph.add_edge(START, "greeting")

graph.add_conditional_edges(
    "random", # Source node
    should_continue, # Routing function
    {
        # Same edges retured by "should_continue" function
        "loop": "random", # self-loop back to same node 
        "exit": END # End of the graph
    }
)

app = graph.compile()
initial_state = AgentState(name="Minal",numbers=[],counter=-1)
print(app.invoke(initial_state))