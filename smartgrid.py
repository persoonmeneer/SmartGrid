from __future__ import annotations
import mesa
from typing import Union, Optional
import csv
from operator import attrgetter
from Agents.cable import Cable
from Agents.house import House
from Agents.battery import Battery
from distribute import distribute
import numpy as np
import pandas as pd
import json
        

class SmartGrid(mesa.Model):
    def __init__(self, district: int) -> None:
        # objects
        self.houses: list[House] = self.add_objects(district, 'houses')
        self.batteries: list[House] = self.add_objects(district, 'batteries')
        self.cables: list[Cable] = []
        self.district = district
        self.information = []

        # total numher of cable
        self.num_cables = 0

        width, height = self.bound()
        self.grid: mesa.space = mesa.space.MultiGrid(width + 1,
                                                     height + 1, False)

        # add houses to grid
        for i in self.houses:
            self.grid.place_agent(i, (i.x, i.y))

        # add batteries to grid
        for i in self.batteries:
            self.grid.place_agent(i, (i.x, i.y))

        # order placement
        self.placement_order()

        # add cables to grid
        self.link_houses()
        self.lay_cable()

        self.get_information()
        

    def bound(self) -> tuple[int, int]:
        """
        This function generates the boundaries of the grid
        Returns:
            tuple[int, int]: the maximum x and y values for the grid
        """

        # find the maximum x and y values of the houses and battery lists
        max_x = max([max(self.houses, key=attrgetter('x'))] +
                    [max(self.batteries, key=attrgetter('x'))],
                    key=attrgetter('x'))
        max_y = max([max(self.houses, key=attrgetter('y'))] +
                    [max(self.batteries, key=attrgetter('y'))],
                    key=attrgetter('y'))

        return (max_x.x, max_y.y)

    def placement_order(self) -> None:
        """
        This function finds the order in which the houses get
        their battery assigned and sort the house list
        """

        for house in self.houses:
            # list of distances to all the batteries
            dist_batteries = []
            for battery in self.batteries:
                # add distance to list
                dist_batteries.append(house.distance(battery))

            # sort the list in ascending order
            dist_batteries.sort()

            # assign priority value to house
            house.priority = dist_batteries[4] - dist_batteries[0]

        # sort houses based on priority
        self.houses.sort(key=lambda x: x.priority, reverse=True)

    def link_houses(self) -> None:
        """
        This function assigns each house to a battery
        """
        # all placed houses
        houses_placed = []
       
        # find closest battery for every house
        for house in self.houses:
            # smallest distance to a battery
            min_dist = -1.0
          
            # boolean to check if the house can connect to a battery
            battery_found = False
          
            # check for all batteries
            for battery in self.batteries:
                # distance to battery
                dist = house.distance(battery)
                # if a connection can be made, remember that
                if min_dist == -1 and house.check_connection(battery):
                    min_dist = dist
                    best_battery = battery
                    battery_found = True
                # if distance to new battery is smaller than minimum, update
                elif min_dist > dist and house.check_connection(battery):
                    min_dist = dist
                    best_battery = battery
                    battery_found = True
           
            # remove house of houses not placed if a battery to connect to
            # is found
            if battery_found:
                # add house to battery and copy all the paths in battery
                best_battery.add_house(house)
                best_battery.copy_all_paths()
           
                houses_placed.append(house)
       
        # get all the houses which are not placed
        self.houses_not_placed = [house for house in self.houses if house not in houses_placed]
        
        
        if len(self.houses_not_placed) > 0:
            distribute(self.batteries, self.houses_not_placed)
                    
    def lay_cable(self) -> None:
        """
        This function connects the houses with the batteries by placing cables
        """

        # unique id for cables
        cable_id = 1000
        
        # create and place the cables for every house
        for house in self.houses:
            # x and y coordinate of the connected battery
            battery = house.connection
                
            if battery.x >= house.x and battery.y <= house.y:
                horizontal = [(i, house.y) for i in range(house.x, battery.x + 1, 1)]
                vertical = [(battery.x, i) for i in np.arange(house.y, battery.y - 1, -1)]
            elif battery.x >= house.x and battery.y >= house.y:
                horizontal = [(i, house.y) for i in range(house.x, battery.x + 1, 1)]
                vertical = [(battery.x, i) for i in range(house.y, battery.y + 1, 1)]
            elif battery.x <= house.x and battery.y >= house.y:   
                horizontal = [(i, house.y) for i in np.arange(house.x, battery.x - 1, -1)] 
                vertical = [(battery.x, i) for i in range(house.y, battery.y + 1, 1)]
            elif battery.x <= house.x and battery.y <= house.y:
                horizontal = [(i, house.y) for i in np.arange(house.x, battery.x - 1, -1)] 
                vertical = [(battery.x, i) for i in np.arange(house.y, battery.y - 1, -1)]
            
            path = horizontal + vertical
            
            # remove the dublicate coordinates at turns
            path = pd.unique(path).tolist()
                          
            for space in path:
                # add cable to the house
                self.addCable(space[0], space[1], house, cable_id)
                cable_id += 1
                
    def addCable(self, x, y, house, cable_id):
        new_cable = Cable(cable_id, self, x, y, house.connection.unique_id)
        new_cable.battery_connection = house.connection
        house.add_cable(new_cable)

        # update number of cables
        self.num_cables += 1

        # place cable in the grid
        self.grid.place_agent(new_cable, (x, y))

    def costs(self) -> int:
        """
        This function calculates the total costs for the cables and batteries
        Returns:
            int: total costs
        """

        cable_cost = self.num_cables * 9
        battery_cost = 5000 * len(self.batteries)

        return cable_cost + battery_cost
    
    def get_information(self) -> None:
        """
        This function creates the representation of the data
        """
        
        # dictionary for general information
        dct = {}
        dct["district"] = self.district
        dct["costs-shared"] = self.costs()
        
        # add general information to information list
        self.information.append(dct)
        
        # for every battery make a dictionary with its information
        for battery in self.batteries:
            # dictionary of battery
            dct = {}
            dct["location"] = str(battery.x) + "," + str(battery.y)
            dct["capacity"] = battery.capacity
            dct["houses"] = []
            
            # for every house make a dictionary with its information
            for house in battery.houses:
                # dictionary for house
                dct_house = {}
                dct_house["location"] = str(house.x) + "," + str(house.y)
                dct_house["output"] = house.energy
                dct_house["cables"] = []
                
                # add location of all cables connected to houses
                # in the dictionary of information houses
                for cable in house.cables:
                    dct_house["cables"].append(str(cable.x) + "," + str(cable.y))
                dct["houses"].append(dct_house)
            
            # add all information to self.information
            self.information.append(dct)
        
    def add_objects(self, district: int, info: str) ->Union[list[House], list[Battery]]:
        """
        Add houses or battery list of district depending on 'info'
        Args:
            district (int): district number
            info (str): 'houses' or 'batteries'
        Returns:
            Union[list[House], list[Battery]]: a list with all the houses or batteries
        """

        # path to data
        path = 'Huizen&Batterijen/district_' + str(district) + '/district-' + str(district) + '_' +  info + '.csv'

        # list with the information
        lst = []

        # add the information to the list
        with open(path, 'r') as csv_file:
            data = csv.reader(csv_file)

            # index to skip header
            count = 0

            # go through all rows except the first
            for line in data:
                # skip header
                if count == 0:
                    count += 1
                    continue

                # convert the data to a neat list with floats
                if not line[0].isnumeric():
                    neat_data = line[0].split(',')
                    line = neat_data + [line[1]]

                # information
                x = int(line[0])
                y = int(line[1])
                energy = float(line[2])

                # append a house or Battery
                if info == 'houses':
                    lst.append(House(count, self, x, y, energy))
                else:
                    lst.append(Battery(count, self, x, y, energy))

                count += 1

        return lst

if __name__ == "__main__":
    test_wijk_1 = SmartGrid(1)
    print(test_wijk_1.costs())
    with open("district1.json", "w") as outfile:
        json.dump(test_wijk_1.information, outfile)

    # test_wijk_2 = SmartGrid(2)
    # print(test_wijk_2.costs())
    # with open("district2.json", "w") as outfile:
    #     json.dump(test_wijk_2.information, outfile)

    # test_wijk_3 = SmartGrid(3)
    # print(test_wijk_3.costs())
    # with open("district3.json", "w") as outfile:
    #     json.dump(test_wijk_3.information, outfile)