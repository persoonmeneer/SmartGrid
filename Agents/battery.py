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
        self.houses: list[House] = []
        self.all_paths = [[(x, y)]]
        self.copy_paths: list[list[tuple[int, int]]] = []
   
    def copy_all_paths(self) -> None:
        self.copy_paths = copy.deepcopy(self.all_paths)
        
    def connect(self) -> None:
        """
        This function will connect all the houses to the Battery
        and will lay all the cables on the best way
        """
       
        # if not all paths are connected, we will connect the closesed paths
        while len(self.all_paths) > 1:
            self.shortersPath()
        # if all paths are connected, draw all the cables
        self.lay_cables(self.all_paths[0])
    def lay_cables(self, path: list[tuple[int, int]]) -> None:
        """
        this function will draw all the cables from the houses to the Battery
        """
       
        # remove duplicates
        path = pd.unique(path)
       
        # create and place the cables
        for i, point in enumerate(path):
            cable = Cable(i + 150*self.unique_id, self.model, point[0], point[1], self.unique_id)
            self.model.grid.place_agent(cable, point)
            self.model.cables.append(cable)
           
        # add all cables to number of cables
        self.model.num_cables += i + 1
    def add_house(self, house: House) -> None:
        """
        this function will add a house to the Battery
        """
       
        # reduce energy of the battery
        self.energy -= house.energy
       
        # append the house to the houses list
        self.houses.append(house)
       
        # connect the house
        house.connect(self)
       
        # append the coordinate of the house to the paths property
        self.all_paths.append([(house.x, house.y)])
  
    def shortersPath(self) -> None:
        """
        this function will check which paths are closesed to each other
        after that it will connect the paths with a path
        """
       
        # initiate minimum distance
        min_dist = -1
       
        # find the shortest path between all paths
        for i, path_1 in enumerate(self.all_paths):
            # stop if at the last path
            if i == len(self.all_paths) - 1:
                break
           
            for not_j, path_2 in enumerate(self.all_paths[i + 1:]):
                # index for second path in self.all_paths
                j = not_j + i + 1
               
                # find the indexes of closest points of 2 paths and the distance
                dist, point_1, point_2 = self.distance_paths(path_1, path_2)
               
                # update data if new minimum is found
                if min_dist == -1 or dist < min_dist:
                    min_dist = dist
                    path_index_1 = i
                    path_index_2 = j
                    best_point_1 = point_1
                    best_point_2 = point_2
 
        # remove the chosen paths oout of the copy list
        self.copy_paths.pop(path_index_2)
        self.copy_paths.pop(path_index_1)
       
        # get best path between the found closest paths
        path = self.getBestPath(best_point_1, best_point_2)
       
        # now connect the paths together
        self.connect_paths(path_index_1, path_index_2, path)
    def connect_paths(self, path_index_1: int, path_index_2: int, path: list[tuple[int, int]]) -> None:
        """
        this function will merge three paths together
        """
      
        # combine both paths and remove duplicates
        self.all_paths[path_index_2] = self.all_paths[path_index_1] + self.all_paths[path_index_2] + path
       
        # delete the old path
        del self.all_paths[path_index_1]
       
        # copy path
        self.copy_paths = copy.deepcopy(self.all_paths)
      
 
    def get_path(self, point_1: tuple[int, int], point_2: tuple[int, int], info: int) -> list[tuple[int, int]]:
        """
        this function will make a pathbetween two points
        """
        # get smallest and biggest x value
        small_x, big_x = min([point_1[0], point_2[0]]), max([point_1[0], point_2[0]])
        # check which coordinate has the smallest y value and put that as starting point
        if point_1[1] < point_2[1]:
            from_x, from_y = point_1[0], point_1[1]
            to_x, to_y = point_2[0], point_2[1]
        else:
            from_x, from_y = point_2[0], point_2[1]
            to_x, to_y = point_1[0], point_1[1]
        battery_found = True
        i = 0
             # make a new path every time a different battery is in the path
        while True:
            # no battery block found yet
            battery_block = False
          
            if info == 1:
                # make the path
                side_step = [(from_x, from_y + j) for j in range(i)]
                horizontal = [(j, from_y + i) for j in range(small_x, big_x)]
                vertical = [(to_x, j) for j in range(from_y + i, to_y + 1)]
            else:
                side_step = [(from_x, j) for j in range(from_y, to_y - i + 1)]
                horizontal = [(j, to_y - i) for j in range(small_x, big_x)]
                vertical = [(to_x, j) for j in range(to_y - i, to_y + 1)]
            path = side_step + horizontal + vertical
            # get all the content of the path
            content = self.model.grid.get_cell_list_contents(path)
            # check if there is a battery in the content of the path
            for battery in self.model.batteries:
                if battery in content and battery.unique_id != self.unique_id:
                    battery_block = True
                    i += 1
                    break
                elif battery == self.model.batteries[-1]:
                    battery_found = False
           
            if not battery_found:
                break
           
        return path
  
    def getBestPath(self, point_1: tuple[int, int], cor_2: tuple[int, int]) -> list[tuple[int, int]]:
        """"
        this function will return the best path that we can draw between
        two coordinates
        """
      
        # get two paths drawn in a different way
        path_1 = self.get_path(point_1, cor_2, 1)
        path_2 = self.get_path(point_1, cor_2, 2)
        # get the distance of both paths
        if len(self.all_paths) <= 2:
            return path_1
       
        #
        dist_1 = self.minDistancePathToAllPaths(path_1)
        dist_2 = self.minDistancePathToAllPaths(path_2)
 
        # check which path is the shorters
        if dist_1 < dist_2:
            return path_1
        return path_2
          
    def minDistancePathToAllPaths(self, path: list[tuple[int, int]]) -> int:
        """
        this function gets the minimal distance from a input path to all the paths
        """
        # initialize minimum distance
        min_dist = -1
       
        for i, other_path in enumerate(self.copy_paths):
            dist, index_1, index_2 = self.distance_paths(other_path, path)
           
            if min_dist == -1 or dist < min_dist:
                min_dist = dist
               
        return min_dist
    def distance_paths(self, path_1: list[tuple[int, int]], path_2: list[tuple[int, int]]) -> tuple[int, tuple[int, int], tuple[int, int]]:
        """
        this function returns the smallest distance between two input paths
        and returns the indexes of both path coordinates which are connected
        """
       
        min_dist = -1
       
        for i, point_1 in enumerate(path_1):
            for j, point_2 in enumerate(path_2):
                dist = self.distance(point_1, point_2)
               
                if min_dist == -1 or dist < min_dist:
                    min_dist = dist
                    best_point_1 = point_1
                    best_point_2 = point_2
                   
        return min_dist, best_point_1, best_point_2
    def distance(self, v: tuple[int, int], w: tuple[int, int]) -> int:
        """
        this function returns the minimal distance between two coordinates
        """
       
        return abs(v[0] - w[0]) + abs(v[1] - w[1])