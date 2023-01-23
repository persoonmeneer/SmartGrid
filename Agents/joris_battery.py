from __future__ import annotations
from Agents.cable import Cable
# from Agents.house import House
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
        self.all_paths = []

    def connectAllHouses(self):
        """
        This function will connect all the houses to the Battery
        and will lay all the cables on the best way
        """
        # if not all paths are connected, we will connect the closesed paths
        while len(self.all_paths) > 1:
            # if len(self.all_paths) == 2:
                # print(self.all_paths)
                # print("break")
            self.shortersPath()
            # print(len(self.all_paths))

        # if all paths are connected, draw all the cables
        self.drawLines(self.all_paths[0])

    def drawLines(self, path: list[tuple(int, int)]):
        """
        this function will draw all the cables from the houses to the Battery
        """
        i = 0
        for cor in path:
            cable = Cable(i + 150*self.unique_id, self.model, cor[0], cor[1], self.unique_id)
            self.model.grid.place_agent(cable, (cor[0], cor[1]))
            self.model.cables.append(cable)
            i += 1
        # add all cables to number of cables
        self.model.num_cables += i

    def addHouse(self, house: House):
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

    # def shortersPathNew(self)
    #     """
    #     this function will check which paths are closesed to each other
    #     after that it will connect the paths with a path
    #     """
    #     # get all the paths
    #     all_paths = self.all_paths
    #     total_paths = len(all_paths)

    #     min_distance = 1000
    #     for i in range(total_paths):
    #         for j in range(i + 1, total_paths):
    #             path_1 = all_paths[i]
    #             path_2 = all_paths[j]

    #             distance, index_1, index_2 = self.distancePaths(path_1, path_2)

    #             if distance < min_distance:
    #                 min_distance = distance
    #                 path_index_1 = [i]
    #                 path_index_2 = [j]
    #                 cor_index_1 = [index_1]
    #                 cor_index_2 = [index_2]
    #             elif distance = min_distance:
    #                 path_index_1.append(i)
    #                 path_index_2.append(j)
    #                 cor_index_1.append(index_1)
    #                 cor_index_2.append(index_2)

        all_indexes = len(parh_index_1)
    #     for i in range(all_indexes):
            
    #     # get best path between the found closest paths
    #     path = self.getBestPath(all_paths[path_index_1][cor_index_1], all_paths[path_index_2][cor_index_2])
    #     # now connect the paths together
    #     self.connectPaths(path_index_1, path_index_2, path)

    def shortersPath(self):
        """
        this function will check which paths are closesed to each other
        after that it will connect the paths with a path
        """
        # get all the paths
        all_paths = self.all_paths
        total_paths = len(all_paths)

        min_distance = 1000
        for i in range(total_paths):
            for j in range(i + 1, total_paths):
                path_1 = all_paths[i]
                path_2 = all_paths[j]

                distance, index_1, index_2 = self.distancePaths(path_1, path_2)

                if distance < min_distance:
                    min_distance = distance
                    path_index_1 = i
                    path_index_2 = j
                    cor_index_1 = index_1
                    cor_index_2 = index_2

        # get best path between the found closest paths
        path = self.getBestPath(all_paths[path_index_1][cor_index_1], all_paths[path_index_2][cor_index_2], path_index_1, path_index_2)
        # now connect the paths together
        self.connectPaths(path_index_1, path_index_2, path)

    def connectPaths(self, path_index_1: int, path_index_2: int, path: list[tuple(int, int)]):
        """
        this function will merge three paths together
        """
        
        # combine both paths
        self.all_paths[path_index_2] = self.all_paths[path_index_1] + self.all_paths[path_index_2] + path
        # delete the old path
        del self.all_paths[path_index_1]
        

    def getPath1(self, cor_1: tuple(int, int), cor_2: tuple(int, int)) -> list[tuple(int, int)]:
        """
        this function will make a pathbetween two points
        """

        # get smallest and biggest x value
        small_x, big_x = min([cor_1[0], cor_2[0]]), max([cor_1[0], cor_2[0]])

        # check which coordinate has the smallest y value and put that as starting point
        if cor_1[1] < cor_2[1]:
            from_y, from_x = cor_1[1], cor_1[0]
            to_x, to_y = cor_2[0], cor_2[1]
        else:
            from_y, from_x = cor_2[1], cor_2[0]
            to_x, to_y = cor_1[0], cor_1[1]

        battery_block = True
        i = 0

    	# make a new path every time a different battery is in the path
        while battery_block == True:
            # no battery block found yet
            battery_block = False
            
            # make the path
            y1 = [(from_x, from_y + j) for j in range(i)]
            x1 = [(j, from_y + i) for j in range(small_x, big_x)]
            y2 = [(to_x, j) for j in range(from_y + i, to_y + 1)]

            cor_arr = y1 + x1 + y2
            # get all the content of the path
            content = self.model.grid.get_cell_list_contents(cor_arr)

            # check if there is a battery in the content of the path
            for bat in self.model.batteries:
                if bat in content and not (bat.x == self.x and bat.y == self.y):
                    battery_block = True
                    i += 1
                    
        return cor_arr

    def getPath2(self, cor_1: tuple(int, int), cor_2: tuple(int, int)) -> list[tuple(int, int)]:
        """
        this function will make a pathbetween two points
        """

        # get smallest and biggest x value
        small_x, big_x = min([cor_1[0], cor_2[0]]), max([cor_1[0], cor_2[0]])

        # check which coordinate has the smallest y value and put that as starting point
        if cor_1[1] < cor_2[1]:
            from_y, from_x = cor_1[1], cor_1[0]
            to_x, to_y = cor_2[0], cor_2[1]
        else:
            from_y, from_x = cor_2[1], cor_2[0]
            to_x, to_y = cor_1[0], cor_1[1]

        battery_block = True
        i = 0

        # make a new path every time a different battery is in the path
        while battery_block == True:
            # no battery block found yet
            battery_block = False
            
            # make the path
            y1 = [(from_x, j) for j in range(from_y, to_y - i)]
            x1 = [(j, to_y - i) for j in range(small_x, big_x)]
            y2 = [(to_x, j) for j in range(to_y - i, to_y + 1)]

            cor_arr = y1 + x1 + y2
            # get all the content of the path
            content = self.model.grid.get_cell_list_contents(cor_arr)

            # check if there is a battery in the content of the path
            for bat in self.model.batteries:
                if bat in content and not (bat.x == self.x and bat.y == self.y):
                    battery_block = True
                    i += 1
        
        return cor_arr
    

    def getBestPath(self, cor_1: tuple(int, int), cor_2: tuple(int, int), path_index_1, path_index_2) -> list[tuple(int, int)]:
        """"
        this function will return the best path that we can draw between
        two coorinates
        """
        
        # get two paths drawn in a different way
        path_1 = self.getPath1(cor_1, cor_2)
        path_2 = self.getPath2(cor_1, cor_2)

        # get the distance of both paths
        if len(self.all_paths) > 2:

            distance_1 = self.minDistancePathToAllPaths(path_1, path_index_1, path_index_2)
            distance_2 = self.minDistancePathToAllPaths(path_2, path_index_1, path_index_2)
     
            # check which path is the shorters
            if distance_1 < distance_2:
                return path_1
                # self.connectCluster(path_1, path_1_index, path)
            else: 
                return path_2
                # self.connectCluster(path_2)
        return path_1
            
    def minDistancePathToAllPaths(self, path: list[tuple(int, int)], path_index_1, path_index_2) -> tuple(int, int, int, int):
        """
        this function gets the minimal distance from a input path to all the paths
        """

        # get all paths
        all_paths = self.all_paths
        total_paths = len(all_paths)
        # print(total_paths)

        min_distance = 1000
        

        # get the smallest distance
        for i in range(total_paths):
            if i == path_index_1 or i == path_index_2:
                continue
            distance, cor_1, cor_2 = self.distancePaths(all_paths[i], path)
            
            if distance < min_distance and distance != 0:

                min_distance = distance
                path_index = i
                cor_index_1 = cor_1
                cor_index_2 = cor_2

        return min_distance, path_index, cor_index_1, cor_index_2

    # def minDistancePathToAllPaths(self, path):
    #     all_paths = self.all_paths
    #     total_paths = len(all_paths)

    #     min_distance = 1000
    #     path_index = []
    #     cor_index_1 = []
    #     cor_index_2 = []

    #     for i in range(total_paths):
    #         distance, cor_1, cor_2 = self.distancePaths(all_paths[i], path)
    #         if distance <= min_distance and distance != 0:

    #             min_distance = distance
    #             path_index.append(i)
    #             cor_index_1.append(cor_1)
    #             cor_index_2.append(cor_2)

    #     return min_distance, path_index, cor_index_1, cor_index_2

    def distancePaths(self, path_1: list[tuple(int, int)], path_2: list[tuple(int, int)]) -> tuple(int, int, int):
        """
        this function returns the smallest distance between two input paths
        and returns the indexes of both path coordinates which are connected
        """
        len_path_1 = len(path_1)
        len_path_2 = len(path_2)

        min_distance = 1000

        for i in range(len_path_1):
            for j in range(len_path_2):
                distance = self.distance(path_1[i], path_2[j])
                if distance < min_distance:
                    min_distance = distance
                    first = i
                    second = j
        return min_distance, first, second

    def distance(self, v: tuple(int, int), w: tuple(int, int)) -> int:
        """
        this function returns the minimal distance between two coordinates
        """
        return abs(v[0] - w[0]) + abs(v[1] - w[1])