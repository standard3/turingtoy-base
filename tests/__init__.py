from typing import (
    Dict,
    List,
    Optional,
    Tuple,
    Any
)


def run_turing_machine(machine: Dict, input_: str, steps: Optional[int] = None) -> Tuple[str, List, bool]:
    # Extract necessary information from the machine dictionary
    tape = list(input_)
    head = 0
    state = machine["start state"]

    execution_history = []
    accepted = False
    print(machine)
    while state not in machine["final states"]:
        symbol = tape[head]
        transition = machine["table"][state][symbol]
        print("transition : %s" %transition)

        execution_history.append({
            "state": state,
            "tape": tape[:head] + [f"[{symbol}]"] + tape[head + 1:],
            "head": head,
            "transition": transition
        })

        if type(transition) != str:
            for action, value in transition.items():
                if action == "write":
                    tape[head] = value
                elif action == "L":
                    head -= 1
                elif action == "R":
                    head += 1
            state = value
        
        else:
            if transition == "L":

                head -=1
            elif transition == "R":

                head +=1

        

        if head < 0:
            tape.insert(0, machine["blank"])
            head = 0
        elif head >= len(tape):
            tape.append(machine["blank"])

    output = "".join(tape).strip()
    accepted = True

    return output, execution_history, accepted


def to_dict(keys: List[str], value: Any) -> Dict[str, Any]:
    return {key: value for key in keys}




machine = {
        "blank": " ",
        "start state": "right",
        "final states": ["done"],
        "table": {
            # Start at the second number's rightmost digit.
            "right": {
                **to_dict(["0", "1", "+"], "R"),
                " ": {"L": "read"},
            },
            # Add each digit from right to left:
            # read the current digit of the second number,
            "read": {
                "0": {"write": "c", "L": "have0"},
                "1": {"write": "c", "L": "have1"},
                "+": {"write": " ", "L": "rewrite"},
            },
            # and add it to the next place of the first number,
            # marking the place (using O or I) as already added.
            "have0": {**to_dict(["0", "1"], "L"), "+": {"L": "add0"}},
            "have1": {**to_dict(["0", "1"], "L"), "+": {"L": "add1"}},
            "add0": {
                **to_dict(["0", " "], {"write": "O", "R": "back0"}),
                "1": {"write": "I", "R": "back0"},
                **to_dict(["O", "I"], "L"),
            },
            "add1": {
                **to_dict(["0", " "], {"write": "I", "R": "back1"}),
                "1": {"write": "O", "L": "carry"},
                **to_dict(["O", "I"], "L"),
            },
            "carry": {
                **to_dict(["0", " "], {"write": "1", "R": "back1"}),
                "1": {"write": "0", "L": "carry"},
            },
            # Then, restore the current digit, and repeat with the next digit.
            "back0": {
                **to_dict(["0", "1", "O", "I", "+"], "R"),
                "c": {"write": "0", "L": "read"},
            },
            "back1": {
                **to_dict(["0", "1", "O", "I", "+"], "R"),
                "c": {"write": "1", "L": "read"},
            },
            # Finish: rewrite place markers back to 0s and 1s.
            "rewrite": {
                "O": {"write": "0", "L": "rewrite"},
                "I": {"write": "1", "L": "rewrite"},
                **to_dict(["0", "1"], "L"),
                " ": {"R": "done"},
            },
            "done": {},
        },}



#print(run_turing_machine(machine, "11+1"))