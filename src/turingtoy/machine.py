"""todo"""

from dataclasses import (
    dataclass,
)
from enum import (
    Enum,
    unique,
)
from typing import (
    List,
)


@unique
class Direction(Enum):
    """Direction to move the tape head."""

    RIGHT = "R"
    LEFT = "L"


@dataclass
class Move:
    """Move the tape head in a direction.

    Attributes:
        direction: direction to move the tape head
        state: state to transition to
    """

    direction: Direction
    state: str


@dataclass
class Write:
    """Write a character to the tape.

    Attributes:
        character: character to write
        direction: direction to move the tape head
    """

    character: str | None
    direction: Direction


@dataclass
class Transition:
    """A transition from one state to another.

    Attributes:
        name: name of the state
        instruction: instruction to execute
    """

    name: str
    instruction: Write | Move


class Machine:
    """A Turing machine.

    This class represents a Turing machine. It validates the machine and runs it.
    The format of the machine is a dictionary with the following keys
    - blank: character to represent a blank cell
    - start state: initial state of the machine
    - final states: list of states that are considered final
    - table: transition table

    Attributes:
        blank: character to represent a blank cell
        start_state: initial state of the machine
        final_states: list of states that are considered final
        table: transition table

    Raises:
        ValueError: if the machine is not valid
    """

    blank: str
    start_state: str
    final_states: List[str]
    table: List[Transition]

    def __init__(self, machine: dict) -> None:
        self.blank = machine["blank"]

        # we must validate the table first, as it is used in the other validations
        self.table = self._validate_table(machine["table"])

        # validate the start state and final states
        self.start_state = self._validate_start_state(machine["start state"])
        self.final_states = self._validate_final_states(machine["final states"])

    def _validate_start_state(self, start_state: str) -> str:
        """Validate start state.

        Args:
            start_state: start state

        Returns:
            start state

        Raises:
            ValueError: if the start state is not in the table
        """
        # Validate that the start state is in the table
        if self.start_state not in self.table:
            raise ValueError("Start state not in transition table")

        return start_state

    def _validate_final_states(self, final_states: List[str]) -> List[str]:
        """Validate final states.

        Args:
            final_states: list of final states

        Returns:
            list of final states

        Raises:
            ValueError: if a final state is not in the table
        """
        # Validate that all final states are in the table
        for final_state in final_states:
            if final_state not in self.table:
                raise ValueError("Final state not in transition table")

        return final_states

    def _validate_table(self, table: dict) -> List[Transition]:
        """Validate the transition table.

        Args:
            table: transition table

        Returns:
            list of Transition objects

        Raises:
            ValueError: if the table is not valid
        """
        # Validate that all states are in the table
        for state in table:
            for symbol in table[state]:
                symbol_dict = table[state][symbol]
                direction = (
                    Direction.LEFT.value
                    if symbol_dict.get(Direction.LEFT.value)
                    else Direction.RIGHT.value
                )

                # Validate that the move symbol is a valid direction
                if direction not in [d.value for d in Direction]:
                    raise ValueError(
                        f"Write symbol for {symbol_dict} must be '{Direction.LEFT.value}' or '{Direction.RIGHT.value}'"
                    )

                # Check write symbol
                if symbol_dict.get("write"):
                    # Validate that the write symbol is a single character
                    if len(symbol_dict["write"]) != 1:
                        raise ValueError(
                            f"Write symbol for {symbol_dict} must be a single character"
                        )

                    # Validate that the write symbol is either 1 or 1
                    if not symbol_dict["write"] in ["0", "1"]:
                        raise ValueError(
                            f"Write symbol for {symbol_dict} must be '0' or '1'"
                        )

                    # Validate that the move state is in table
                    if symbol_dict[direction] not in table:
                        raise ValueError(
                            f"Move state for symbole {symbol_dict} not in transition table"
                        )

                # Check move symbol
                else:
                    # Validate that the move symbol is a single character
                    if len(direction) != 1:
                        raise ValueError(
                            f"Move symbol for {symbol_dict} must be a single character"
                        )

                    # Validate that the move symbol is a valid direction
                    if direction not in [d.value for d in Direction]:
                        raise ValueError(
                            f"Move symbol for {symbol_dict} must be 'L' or 'R'"
                        )

        # Convert table to a list of Transition objects
        return self._convert_table(table)

    def _convert_table(self, table: dict) -> List[Transition]:
        """Convert the table to a list of Transition objects.

        Args:
            table: transition table

        Returns:
            list of Transition objects
        """
        transitions = []

        for state, symbols in table.items():
            for symbol, actions in symbols.items():
                instruction = None

                # This is a write symbol
                if "write" in actions:
                    instruction = Write(
                        character=actions["write"],
                        direction=Direction[actions["write"]],
                    )
                # This is a move symbol
                else:
                    direction = (
                        Direction.LEFT if Direction.LEFT in actions else Direction.RIGHT
                    )
                    instruction = Move(
                        direction=direction,
                        state=actions[direction],
                    )

                transitions.append(Transition(name=state, instruction=instruction))

        return transitions
