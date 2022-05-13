from pathlib import (
    Path,
)
from typing import (
    Any,
    Dict,
    List,
)

import pytest

from tests.utils import (
    regression_test,
)
from turingtoy import (
    run_turing_machine,
)


def test_turing_machine_double_1(
    request: pytest.FixtureRequest, global_datadir: Path
) -> None:
    machine = {
        "blank": "0",
        "start state": "e1",
        "final states": ["done"],
        "table": {
            "e1": {
                "0": {"L": "done"},
                "1": {"write": "0", "R": "e2"},
            },
            "e2": {
                "1": {"write": "1", "R": "e2"},
                "0": {"write": "0", "R": "e3"},
            },
            "e3": {
                "1": {"write": "1", "R": "e3"},
                "0": {"write": "1", "L": "e4"},
            },
            "e4": {
                "1": {"write": "1", "L": "e4"},
                "0": {"write": "0", "L": "e5"},
            },
            "e5": {
                "1": {"write": "1", "L": "e5"},
                "0": {"write": "1", "R": "e1"},
            },
            "done": {},
        },
    }

    datadir = global_datadir / "double_1"

    input_ = "111"
    output, execution_history, accepted = run_turing_machine(machine, input_)
    assert output == "1110111"
    assert accepted

    regression_test(
        {
            "machine": machine,
            "input": input_,
            "output": output,
            "execution_history": execution_history,
        },
        datadir / f"{input_}.json",
        request.config.getoption("force_regen"),
    )

    input_ = "1"
    output, execution_history, accepted = run_turing_machine(machine, "1")
    assert output == "101"
    assert accepted

    regression_test(
        {
            "machine": machine,
            "input": input_,
            "output": output,
            "execution_history": execution_history,
        },
        datadir / f"{input_}.json",
        request.config.getoption("force_regen"),
    )


def test_turing_machine_add_two_binary_numbers(
    request: pytest.FixtureRequest, global_datadir: Path
) -> None:
    # Adds two binary numbers together.

    # Format: Given input a+b where a and b are binary numbers,
    # leaves c b on the tape, where c = a+b.
    # Example: '11+1' => '100 1'.
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
        },
    }

    datadir = global_datadir / "add_two_binary_numbers"

    input_ = "11+1"
    output, execution_history, accepted = run_turing_machine(machine, input_)
    assert output == "100 1"
    assert accepted

    regression_test(
        {
            "machine": machine,
            "input": input_,
            "output": output,
            "execution_history": execution_history,
        },
        datadir / f"{input_}.json",
        request.config.getoption("force_regen"),
    )

    input_ = "1011+11001"
    output, execution_history, accepted = run_turing_machine(machine, input_)
    assert output == "100100 11001"
    assert accepted

    regression_test(
        {
            "machine": machine,
            "input": input_,
            "output": output,
            "execution_history": execution_history,
        },
        datadir / f"{input_}.json",
        request.config.getoption("force_regen"),
    )


def test_turing_machine_binary_multiplication(
    request: pytest.FixtureRequest, global_datadir: Path
) -> None:
    # Multiplies two binary numbers together.

    # Examples: '11*11' => '1001', '111*110' => '101010'.
    machine = {
        "blank": " ",
        "start state": "start",
        "final states": ["done"],
        "table": {
            # Prefix the input with a '+', and go to the rightmost digit.
            "start": {
                **to_dict(["0", "1"], {"L": "init"}),
            },
            "init": {
                " ": {"write": "+", "R": "right"},
            },
            "right": {
                **to_dict(["0", "1", "*"], "R"),
                " ": {"L": "readB"},
            },
            # Read and erase the last digit of the multiplier.
            # If it's 1, add the current multiplicand.
            # In any case, double the multiplicand afterwards.
            "readB": {
                "0": {"write": " ", "L": "doubleL"},
                "1": {"write": " ", "L": "addA"},
            },
            "addA": {
                **to_dict(["0", "1"], "L"),
                "*": {"L": "read"},  # enter adder
            },
            # Double the multiplicand by appending a 0.
            "doubleL": {
                **to_dict(["0", "1"], "L"),
                "*": {"write": "0", "R": "shift"},
            },
            "double": {  # return from adder
                **to_dict(["0", "1", "+"], "R"),
                "*": {"write": "0", "R": "shift"},
            },
            # Make room by shifting the multiplier right 1 cell.
            "shift": {
                "0": {"write": "*", "R": "shift0"},
                "1": {"write": "*", "R": "shift1"},
                " ": {"L": "tidy"},  # base case: multiplier = 0
            },
            "shift0": {
                "0": {"R": "shift0"},
                "1": {"write": "0", "R": "shift1"},
                " ": {"write": "0", "R": "right"},
            },
            "shift1": {
                "0": {"write": "1", "R": "shift0"},
                "1": {"R": "shift1"},
                " ": {"write": "1", "R": "right"},
            },
            "tidy": {
                **to_dict(["0", "1"], {"write": " ", "L": "tidy"}),
                "+": {"write": " ", "L": "done"},
            },
            "done": {},
            # This is the 'binary addition' machine almost verbatim.
            # It's adjusted to keep the '+'
            # and to lead to another state instead of halting.
            "read": {
                "0": {"write": "c", "L": "have0"},
                "1": {"write": "c", "L": "have1"},
                "+": {"L": "rewrite"},  # keep the +
            },
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
            "back0": {
                **to_dict(["0", "1", "O", "I", "+"], "R"),
                "c": {"write": "0", "L": "read"},
            },
            "back1": {
                **to_dict(["0", "1", "O", "I", "+"], "R"),
                "c": {"write": "1", "L": "read"},
            },
            "rewrite": {
                "O": {"write": "0", "L": "rewrite"},
                "I": {"write": "1", "L": "rewrite"},
                **to_dict(["0", "1"], "L"),
                " ": {"R": "double"},  # when done, go to the 'double' state
            },
        },
    }

    datadir = global_datadir / "binary_multiplication"

    input_ = "11*101"
    output, execution_history, accepted = run_turing_machine(machine, input_)
    assert output == "1111"
    assert accepted

    regression_test(
        {
            "machine": machine,
            "input": input_,
            "output": output,
            "execution_history": execution_history,
        },
        datadir / "11x101.json",
        request.config.getoption("force_regen"),
    )


def to_dict(keys: List[str], value: Any) -> Dict[str, Any]:
    return {key: value for key in keys}
