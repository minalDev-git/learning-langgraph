from typing import TypedDict
from langgraph.graph import StateGraph #framework that helps you design and manage the flow of tasks in your app using a graph

# Simplest langgraph we can create: START ----> NODE -----> END
# WE created Single Node and Single input graph here

# we now create an AgentState (Application's State) --> shared data structure that keeps track of information as your app runs
class AgentState(TypedDict): # --> state needs to be in the form of TypedDict that's why we inherit it with this.
    message : str

# Defining the very first Node --> it's a very simple normal python func
# we need to pass an input type and output type for a Node (which would both be "State") b/c state tracks the app info
def greeting_node(state: AgentState) -> AgentState: # we need to output the updated state (hence the return type is AgentState)
    """A simple node that adds a greeting message to the state"""

    # Accessing the "message" part in AgentState and update it
    state['message'] = "Hey " + state['message'] + ", How is your day going?"

    return state

# Building a graph using "AgentState" schema
graph = StateGraph(AgentState)

# Adding a node to the graph
# pass the name of your node and the action it will perform in add_node func
graph.add_node("greeter", greeting_node)

# defines the START point of langgraph. START node and the first node are connected using an edge
graph.set_entry_point("greeter") # takes 1 param "key" which is the name of your node which you want the start node to connect to
# defines the FINISH point of langgraph FINISH node and the last node are connected using an edge
graph.set_finish_point("greeter") 

app = graph.compile() #compiles the graph

# Note: Just becuz the graph compiled without any errors, doen't always mean it will successfully run
# Invoking the Graph
result = app.invoke({"message":"Bob"})
#To get the value of "result", we need to reference a certain attribute (in this case its only "message")
print(result["message"])

#  Graph Visualization code
# from IPython.display import Image, display
# display(Image(app.get_graph().draw_mermaid_png()))