from langgraph.graph import StateGraph
from typing import TypedDict, List

class AgentState(TypedDict):
    name: str
    age: str
    skills: List[str]
    final: str

def first_node(state:AgentState)->AgentState:
    """This node greets the user"""

    state['final'] = f"{state['name']}, Welcome to the system! "
    return state

def second_node(state:AgentState)->AgentState:
    """This node describes the user's age"""

    state['final'] = state['final'] + f"You are {state['age']} years old!"
    return state

def third_node(state:AgentState)->AgentState:
    """This node lists the user's skills in a formatted string"""
    
    state['final'] = state['final'] + f" You have skills in: {', '.join(state['skills'])}"
    return state

graph = StateGraph(AgentState)

graph.add_node("personalize", first_node)
graph.add_node("age_description", second_node)
graph.add_node("skills_description", third_node)

graph.add_edge("personalize","age_description")
graph.add_edge("age_describe","skills_description")

graph.set_entry_point("personalize")
graph.set_finish_point("skills_description")

app = graph.compile()
answer = app.invoke({"name":"Bob","age":"32","skills":["Python","Machine Learning", "LangGraph"],"final":""})
print(answer["final"])