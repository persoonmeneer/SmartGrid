 
from __future__ import annotations
from Agents.cable import Cable
import copy
import mesa
import copy
import pandas as pd
 
class Battery(mesa.Agent):
    def __init__(self, unique_id: int, model: mesa.model,
                 x: int, y: int, energy: float) -> None:
        super().__init__(unique_id, model)
        self.x = x  # x coordinate
        self.y = y  # y coordinate
        self.capacity = energy  # total capacity of battery
        self.energy = energy  # remaining energy
        self.houses: list[House] = [] #
        self.all_paths = [[(x, y)]]
        self.copy_paths: list[list[tuple[int, int]]] = []
    
    def copy_all_paths(self) -> None:
        """
        This function deepcopy's all paths of battery
        """
        
        self.copy_paths = copy.deepcopy(self.all_paths)
 
    def lay_cables(self) -> int:
        """
        This function will draw all the cables from the houses to the Battery
        """
        
        # remove duplicates
        path = pd.unique(self.all_paths[0])
        
        # create and place the cables
        for i, point in enumerate(path):
            # create new cable
            cable = Cable(i + 150*self.unique_id, self.model, point[0], point[1], self.unique_id)
            
            # place cable in grid
            self.model.grid.place_agent(cable, point)
            
            # add cable to the model's cable list
            self.model.cables.append(cable)
            
        # add all cables to number of cables
        return i + 1
 
    def add_house(self, house: House) -> None:
        """
        This function adds a not connected house

        Args:
            house (House): a not connected house
        """
        
        # reduce energy of the battery
        self.energy -= house.energy
        
        # append the house to the houses list
        self.houses.append(house)
        
        # connect the house
        house.connect(self)
        
        # append the coordinate of the house to the paths property
        self.all_paths.append([(house.x, house.y)])
 
    def remove_house(self, house: House) -> None:
        """
        This function removes a house from the battery

        Args:
            house (House): a connected house
        """
        
        # remove house from the houses list
        self.houses.remove(house)
        
        # add the house's energy to the battery's energy
        self.energy += house.energy
        
        # remove the house coordinates from the paths
        self.all_paths.remove([(house.x, house.y)])
        
        # remove connection
        house.connection = None
    
    def get_len_paths(self) -> int:
        """
        This function gives the length of the remaining paths

        Returns:
            int: number of paths remaining
        """
        
        return len(self.all_paths)
