"""
This program creates a cable class
"""

from __future__ import annotations
import mesa


class Cable(mesa.Agent):
    """
    Cable agent that connects houses to batteries.
    """
    def __init__(self, unique_id: int, model: mesa.Model,
                 x: int, y: int, battery_id: int) -> None:
        """
        Creates a cable agent with a unique id that has a x and y coordinate.
        Also tracks to which battery it connects.

        Args:
            unique_id (int): unique id of the cable.
            model (mesa.Model): model the agent belongs to.
            x (int): x coordinate of the agent.
            y (int): y coordinate of the agent.
            battery_id (int): id of the battery to which the cable connects.
        """

        super().__init__(unique_id, model)
        self.x = x
        self.y = y
        self.battery_connection = None
        self.battery_id = battery_id
