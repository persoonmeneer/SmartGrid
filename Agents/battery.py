from __future__ import annotations
import mesa

class Battery(mesa.Agent):
    def __init__(self, unique_id: int, model: mesa.model,
                 x: int, y: int, energy: float) -> None:
        super().__init__(unique_id, model)
        self.x = x  # x coordinate
        self.y = y  # y coordinate
        self.capacity = energy  # total capacity of battery
        self.energy = energy  # remaining energy
        self.houses: list[House] = []