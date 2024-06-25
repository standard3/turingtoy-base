"""Turing machine implementation.

This module contains the implementation of a Turing machine.
It is validated and run by the `Machine` class.

Classes:
    Machine: a Turing machine
    State: a state of the machine
    Transition: a transition from one state to another
    Write: write a character to the tape
    Move: move the tape head in a direction
    Direction: direction to move the tape head

Exceptions:
    ValueError: if the machine is not valid
"""

from dataclasses import (
    dataclass,
)
from enum import (
    Enum,
    unique,
)
from typing import (
    Dict,
    List,
    Tuple,
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
    next_state: str


@dataclass
class Transition:
    """A transition from one state to another.

    Attributes:
        symbol: symbol to transition on
        instruction: instruction to execute
    """

    symbol: str
    instruction: Write | Move


@dataclass
class State:
    """A state of the machine.

    Attributes:
        name: name of the state
        transitions: list of transitions
    """

    name: str
    transitions: List[Transition]


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
    table: List[State]

    def __init__(
        self,
        machine: Dict,
    ) -> None:
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
        for state in self.table:
            if state.name == start_state:
                return start_state

        raise ValueError("Start state not in transition table")

    def _validate_final_states(self, final_states: List[str]) -> List[str]:
        """Validate final states.

        Args:
            final_states: list of final states

        Returns:
            list of final states

        Raises:
            ValueError: if a final state is not in the table
        """
        tmp = final_states.copy()

        # Validate that all final states are in the table
        for state in self.table:
            if state.name in final_states:
                tmp.remove(state.name)

        if not tmp:
            return final_states

        raise ValueError("Final state not in transition table")

    def _validate_table(self, table: dict) -> List[State]:
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

    def _convert_table(self, table: dict) -> List[State]:
        """Convert the table to a list of State objects.

        Args:
            table: state table

        Returns:
            list of State objects
        """
        states = []

        for state, symbols in table.items():
            transitions = []

            for symbol, actions in symbols.items():
                instruction = None
                direction = (
                    Direction.RIGHT
                    if actions.get(Direction.RIGHT.value)
                    else Direction.LEFT
                )

                # write symbol
                if "write" in actions:
                    instruction = Write(
                        character=actions["write"],
                        direction=direction,
                        next_state=actions[direction.value],
                    )
                # move symbol
                else:
                    instruction = Move(
                        direction=direction,
                        state=actions[direction.value],
                    )

                transitions.append(Transition(symbol=symbol, instruction=instruction))

            states.append(State(name=state, transitions=transitions))

        return states

    def _validate_input(self, input_: str) -> str:
        """Validate the input.

        Args:
            input_: input to the machine

        Raises:
            ValueError: if the input contains invalid characters
        """
        # Validate that the input only contains 0 and 1
        if not all(c in ["0", "1", "+", "*"] for c in input_):
            raise ValueError("Input must only contain '0' and '1'")

        return input_

    def run(self, input_: str, steps: int | None = None) -> Tuple[str, List, bool]:
        """Run the Turing machine.

        Args:
            input_: input to the machine
            steps: maximum number of steps to run

        Returns:
            Content of the tape after the machine halts. This is a tuple of the content of
            the tape, the execution history, and whether the machine has halted in a final state.
        """
        machine_input = self._validate_input(input_)

        tape = list(machine_input)
        tape.extend([self.blank] * 10)

        state = self.start_state
        position = 0
        execution_history = []

        for _ in range(steps) if steps else range(1000):
            # Find the transition for the current state and symbol
            transition = next(
                (
                    t
                    for t in self.table[state].transitions
                    if t.symbol == tape[position]
                ),
                None,
            )

            # If there is no transition, the machine halts
            if not transition:
                break

            # Execute the instruction
            if isinstance(transition.instruction, Write):
                tape[position] = transition.instruction.character
                state = transition.instruction.next_state
                position += (
                    1 if transition.instruction.direction == Direction.RIGHT else -1
                )
            else:
                state = transition.instruction.state
                position += (
                    1 if transition.instruction.direction == Direction.RIGHT else -1
                )

            execution_history.append((state, tape[:], position))

            # Check if the machine has halted in a final state
            if state in self.final_states:
                break

        return "".join(tape), execution_history, state in self.final_states
