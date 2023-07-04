from typing import (
    Dict,
    List,
    Literal,
    Optional,
    Tuple,
    TypedDict,
    Union,
)

import poetry_version

__version__ = poetry_version.extract(source_file=__file__)


Movement = Literal["L", "R"]
Action = Literal["write", Movement]
Instruction = Union[Movement, Dict[Action, str]]
TransitionTable = Dict[str, Dict[str, Instruction]]
TuringMachine = TypedDict(
    "TuringMachine",
    {
        "blank": str,
        "start state": str,
        "final states": List[str],
        "table": TransitionTable,
    },
)


class HistoryEntry(TypedDict):
    """History entry of a Turing machine step for logging purposes."""

    state: str
    reading: str
    position: int
    memory: str
    transition: Instruction


def run_turing_machine(
    machine: TuringMachine,
    input_: str,
    steps: Optional[int] = None,
) -> Tuple[str, List, bool]:
    trans_table = machine["table"]
    final_states = machine["final states"]
    blank = machine["blank"]

    # Initialize tape with input
    mem: list[str] = list(input_)
    history: List[HistoryEntry] = []  # noqa: F821
    state = machine["start state"]
    pos = 0
    steps_taken = 0

    while state not in final_states:
        if steps is not None and steps_taken >= steps:
            # Maximum number of steps reached: halt
            break

        if pos < 0:
            # Shift tape to the right and insert blank symbol
            mem.insert(0, blank)
            pos = 0
        elif pos >= len(mem):
            # Add blank symbol to end of tape
            mem.append(blank)

        symbol = mem[pos]

        if state not in trans_table or symbol not in trans_table[state]:
            # Missing transition: halt
            break

        instruction = trans_table[state][symbol]

        history.append(
            HistoryEntry(
                state=state,
                reading=symbol,
                position=pos,
                memory="".join(mem),
                transition=instruction,
            )
        )

        if instruction == "L":
            pos -= 1
        elif instruction == "R":
            pos += 1
        else:
            if "write" in instruction:
                mem[pos] = instruction["write"]

            if "L" in instruction:
                pos -= 1
                state = instruction["L"]
            elif "R" in instruction:
                pos += 1
                state = instruction["R"]
            else:
                # Missing movement instruction: halt
                pos += 0  # Necessary for test coverage to see this branch
                break

        steps_taken += 1

    return "".join(mem).strip(blank), history, state in final_states


del poetry_version, Dict, List, Literal, Optional, Tuple, TypedDict, Union 
