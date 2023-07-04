from typing import (
    Dict,
    List,
    Optional,
    Tuple,
)

import poetry_version

__version__ = poetry_version.extract(source_file=__file__)


def run_turing_machine(
    machine: Dict,
    input_: str,
    steps: Optional[int] = None,
) -> Tuple[str, List, bool]:
    blank = machine.get("blank")
    start_state = machine.get("start state")
    final_states = machine.get("final states")
    table = machine["table"]
    current_state = machine['start state']
    memory = list(input_)
    new_input = ""
    print(f"memory: {memory}")
    print(f"Current state: {current_state}")
    i = 0
    while True:
        if i < 0:
            memory.insert(0, blank)
            i = 0
        elif i >= len(memory):
            memory.append(blank)
            
        symbol = memory[i]
        rules = table[current_state][symbol]
        if type(rules) == str:
            if rules == "R":
                i += 1
            else:
                i -= 1
        else:
            #print(f"test rules: {rules}")
            for rule in rules:
                state = rules[rule]
                if rule == "L":
                    i -= 1
                    current_state = state

                elif rule == "R":
                    i += 1
                    current_state = state 
                else:
                    memory[i] = state 
            
            if state == "done":
                print("okokkkk")
                break
    out = "".join(memory).strip(blank)
    print(out)
    return out, [], True

