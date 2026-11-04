# Simple Graph
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal
import random

class State(TypedDict):
    graph_state : str

# Node: Functions that modify the state
def node_1(state : State)-> State:
    print("____Node 1____")
    return {"graph_state" : state["graph_state"] + " I am"}

def node_2(state : State)-> State:
    print("____Node 2____")
    return {"graph_state" : state["graph_state"] + " happy"}

def node_3(state : State)-> State:
    print("____Node 3____")
    return {"graph_state" : state["graph_state"] + " sad"}

# Conditional Edge: Function tells what node to go to next
def decide_mood(state: State) ->Literal["node_2","node_3"]:

    # often we will use state to decide on the next node to visit
    user_input = state["graph_state"]

    # here, let's do a 50/50 split b/w nodes 2, 3
    if random.random() < 0.5:

        # 50% of the time we return Node 2
        return "node_2"

    # 50% of the time we return Node 3
    return "node_3"

#  Build graph
builder = StateGraph(State)

builder.add_node("node_1",node_1)
builder.add_node("node_2",node_2)
builder.add_node("node_3",node_3)

# Logic
builder.add_edge(START,"node_1")
builder.add_conditional_edges(
    "node_1",
    decide_mood, # decide mood use random no.s to decide whether to go to node_2 or node_3
)
builder.add_edge("node_2",END)
builder.add_edge("node_3",END)

graph = builder.compile()
graph.invoke({"graph_state":"Hi, this is minal"})