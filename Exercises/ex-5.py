import random
from typing import TypedDict,List
from langgraph.graph import StateGraph, START, END

class AgentState(TypedDict):
    player_name: str
    rand_num: int
    guesses: List[int]
    attempts: int
    lower_bound: int
    upper_bound: int

def setup_node(state:AgentState)->AgentState:
    """This node setups the lower and upper bound"""

    state['lower_bound'] = 1
    state['upper_bound'] = 20
    state['attempts'] = 0
    state['rand_num'] = random.randint(state['lower_bound'],state['upper_bound'])
    print(state['rand_num'])

    return state

def guess_node(state:AgentState)->AgentState:
    """This node guesses the random number"""
    state['guesses'].append(random.randint(state['lower_bound'],state['upper_bound']))
    state['attempts'] += 1

    return state

def should_continue(state: AgentState):
    """Function to decide what to next"""

    # First, check if the last guess was correct and exit early
    if state['guesses'] and state['guesses'][-1] == state['rand_num']:
        return "end"

    # Otherwise, continue looping while attempts remain
    if state['attempts'] < 7:
        print("ENTERING_LOOP", state['attempts'])
        return "loop"  # Continue looping
    else:
        return "end"  # Exit when attempts exhausted


def hint_node(state:AgentState)->AgentState:
    """Gives hint to the graph"""
    guess = state['guesses'][-1]
    if guess < state['rand_num']:
        print(f"Hint: The number {guess} is too low. Try higher!")
        # exclude the guessed value from the new lower bound
        state['lower_bound'] = guess + 1
    elif guess > state['rand_num']:
        print(f"Hint: The number {guess} is too high. Try lower!")
        # exclude the guessed value from the new upper bound
        state['upper_bound'] = guess - 1

    return state

graph = StateGraph(AgentState)
graph.add_node("setup", setup_node)
graph.add_node("guess",guess_node)
graph.add_node("hint",hint_node)

graph.add_edge(START, "setup")
graph.add_edge("setup","guess")
graph.add_edge("guess","hint")

graph.add_conditional_edges(
    "hint",
    should_continue,
    {
        "loop": "guess",
        "end": END
    }
)

app = graph.compile()
initial_state = AgentState(player_name="Minal",rand_num=0, guesses=[],attempts=0, lower_bound=1,upper_bound=20)
print(app.invoke(initial_state))