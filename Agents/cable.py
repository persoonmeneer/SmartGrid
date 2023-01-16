from __future__ import annotations
import mesa
from Agents.battery import Battery

class Cable(mesa.Agent):
    def __init__(self, unique_id: int, model: mesa.Model,
                 x: int, y: int) -> None:
        super().__init__(unique_id, model)
        self.x = x  # x coordinate
        self.y = y  # y coordinate
        self.battery_connection: Battery = Battery(0, 0, 0, 0, 0)