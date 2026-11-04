from typing import TypedDict, List
from langgraph.graph import StateGraph
import math

class AgentState(TypedDict):
    values: List[int]
    name: str
    operation: str
    result: str

def perform_operation(state:AgentState)->AgentState:
    """This fuctions performs operations on the List"""

    if(state['operation'] == '+'):
        state['result'] = f"Hi {state['name']}, your answer is: {sum(state['values'])}"

    elif (state['operation'] == '*'):
        state['result'] = f"Hi {state['name']}, your answer is: {math.prod(state['values'])}"

    return state

graph = StateGraph(AgentState)
graph.add_node("airthmetic_op", perform_operation)
graph.set_entry_point("airthmetic_op")
graph.set_finish_point("airthmetic_op")

app = graph.compile()
answer = app.invoke({"values":[1,2,3,4],"name":"Jack Sparrow","operation":'*',"result":""})
print(answer["result"])