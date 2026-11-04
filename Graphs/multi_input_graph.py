# WE created Single Node and Multiple inputs graph here. we'll be able to pass multiple inputs in the graph
# we'll create a processing node that performs operations on list data
# Invoke the graph with structure inputs and retrieve outputs

from typing import TypedDict, List
from langgraph.graph import StateGraph

# multiple inputs means multiple keys diff data structures and datatypes
class AgentState(TypedDict):
    values: List[int]
    name: str
    result: str

def processing_values(state: AgentState)-> AgentState:
    """This fuction handles multiple different inputs"""

    state['result'] = f"Hi there, {state['name']}! Your sum = {sum(state['values'])}"
    return state

graph = StateGraph(AgentState)
graph.add_node("processor", processing_values)
graph.set_entry_point("processor")
graph.set_finish_point("processor")

app = graph.compile()
answer = app.invoke({"values":[1,2,3,4],"name":"Bob","result":""})
print(answer["result"])

