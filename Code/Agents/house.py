"""
This program creates a house class
"""

from __future__ import annotations
from Agents.battery import Battery
import mesa


class House(mesa.Agent):
    """
    House agent that has an energy level. The house agent will be connected to
    a battery with enough capacity.
    """
    def __init__(self, unique_id: int, model: mesa.model,
                 x: int, y: int, energy: float) -> None:
        """
        Creates a house agent with a unique id and a x and y coordinate.
        The house has energy output and is intiliazed without battery.

        Args:
            unique_id (int): unique id.
            model (mesa.model): model the agent belongs to.
            x (int): x coordinate.
            y (int): y coordinate.
            energy (float): energy output of the house.
        """
        super().__init__(unique_id, model)
        self.x = x
        self.y = y
        self.energy = energy

        # initialize connection, cable list and priority level
        self.connection: Battery = None
        self.cables = []
        self.priority: float = 0

    def add_cable(self, cable) -> None:
        """
        Adds a cable to the house's cable list
        """

        self.cables.append(cable)

    def distance(self, other: Battery) -> float:
        """
        Function that returns the Manhattan distance between the house
        and the specified battery.

        Args:
            other (Battery): A battery agent.

        Returns:
            float: Manhattan distance between the house and battery.
        """

        return abs(self.x - other.x) + abs(self.y - other.y)

    def connect(self, other: Battery) -> None:
        """
        Reduces the remaining energy in the battery

        Args:
            other (Battery): A House with energy
        """
        self.connection = other

    def check_connection(self, other: Battery) -> bool:
        """
        Function that checks whether the specified battery has enough
        capacity for the house to join.

        Args:
            other (Battery): A battery agent

        Returns:
            bool: Returns True when the house is able to connect, else false.
        """

        if other.energy - self.energy >= 0:
            return True
        return False
