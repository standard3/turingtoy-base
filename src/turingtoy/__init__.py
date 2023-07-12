from typing import Dict, List, Literal, Optional, Tuple, TypedDict, Union

import poetry_version


Movement = Literal["L", "R"]
Action = Literal["write", Movement]
Instruction = Union[Movement, Dict[Action, str]]
TransitionTable = Dict[str, Dict[str, Instruction]]
TuringMachine = TypedDict(
    "TuringMachine",
    {
        "blank": str,
        "start_state": str,
        "final_states": List[str],
        "table": TransitionTable,
    },
)


class Entry(TypedDict):
    state: str
    reading: str
    position: int
    tape: str
    transition: Instruction


def simulate_turing_machine(
    machine: TuringMachine,
    input_: str,
    steps: Optional[int] = None,
) -> Tuple[str, List[Entry], bool]:
    transition_table = machine["table"]
    final_states = machine["final_states"]
    blank_symbol = machine["blank"]

    # Initialize tape with input
    tape: List[str] = list(input_)
    history: List[Entry] = []
    state = machine["start_state"]
    position = 0
    steps_taken = 0
    
    while state not in final_states:
        if steps is not None and steps_taken >= steps:
            # Maximum number of steps reached: halt
            break

        if position < 0:
            # Shift tape to the right and insert blank symbol
            tape.insert(0, blank_symbol)
            position = 0
        elif position >= len(tape):
            # Add blank symbol to end of tape
            tape.append(blank_symbol)

        symbol = tape[position]

        if state not in transition_table or symbol not in transition_table[state]:
            # Missing transition: halt
            break

        instruction = transition_table[state][symbol]

        history_entry: Entry = {
            "state": state,
            "reading": symbol,
            "position": position,
            "tape": "".join(tape),
            "transition": instruction,
        }
        history.append(history_entry)

        if instruction == "L":
            position -= 1
        elif instruction == "R":
            position += 1
        else:
            if "write" in instruction:
                tape[position] = instruction["write"]

            if "L" in instruction:
                position -= 1
                state = instruction["L"]
            elif "R" in instruction:
                position += 1
                state = instruction["R"]
            else:
                # Missing movement instruction: halt
                position += 0  # Necessary for test coverage to see this branch
                break

        steps_taken += 1

    final_tape = "".join(tape).strip(blank_symbol)
    halted = state in final_states

    return final_tape, history, halted


__version__ = poetry_version.extract(source_file=__file__)
del poetry_version, Dict, List, Literal, Optional, Tuple, TypedDict, Union

