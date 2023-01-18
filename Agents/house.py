from __future__ import annotations
import mesa
from Agents.battery import Battery

class House(mesa.Agent):
    def __init__(self, unique_id: int, model: mesa.model,
                 x: int, y: int, energy: float) -> None:
        super().__init__(unique_id, model)
        self.x = x  # x coordinate
        self.y = y  # y coordinate
        self.energy = energy  # energy level

        # initialize connection, cable list and priority level
        self.connection: Battery = Battery(0, 0, 0, 0, 0)
        self.cables: list[Cable] = []
        self.priority: float = 0

    def addCable(self, cable: Cable):
        self.cables.append(cable)

    def distance(self, other: Battery) -> float:
        return abs(self.x - other.x) + abs(self.y - other.y)

    def connect(self, other: Battery) -> None:
        """
        Reduces the remaining energy in the battery

        Args:
            other (House): A House with energy
        """

        other.energy -= self.energy
        self.connection = other

    def check_connection(self, other: Battery) -> bool:
        if other.energy - self.energy >= 0:
            return True
        return False