from typing import (
    Dict,
    List,
    Optional,
    Tuple,
)

import poetry_version

from turingtoy.machine import (
    Machine,
)

__version__ = poetry_version.extract(source_file=__file__)


def run_turing_machine(
    machine: Dict,
    input_: str,
    steps: Optional[int] = None,
) -> Tuple[str, List, bool]:
    """Run a Turing machine.

    Args:
        machine: Turing machine to run
        input_: input to the machine, it is the content at the beginning of the tape
        steps: maximum number of steps to run, if None run until the machine halts

    Returns:
        output: content of the tape after the machine halts. This is a tuple of the content of
        the tape, the execution history, and whether the machine has halted in a final state.
    """

    machine = Machine(machine)

    return ("", [], False)
