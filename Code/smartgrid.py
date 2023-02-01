"""
This program runs smartgrid simulations depending on the users inpu
"""

from __future__ import annotations
from Additional_code.simulated_annealing import optimization
from Additional_code.distribute import distribute
from Additional_code.place_battery import cluster_funct
from Additional_code.visualisation import plot_annealing, visualisation
from Additional_code.lay_cables import create_merged_path
from Agents.battery import Battery
from Agents.house import House
from Agents.cable import Cable
from typing import Union, Any, Tuple, List
from operator import attrgetter
import numpy as np
import pandas as pd
import random
import mesa
import csv
import json
import copy


class SmartGrid(mesa.Model):
    def __init__(self, district: int, version: str, iterations: int) -> None:
        # objects
        self.houses: list[House] = self.add_objects(district, 'houses')

        # which version we want to use
        self.version = version
        self.iterations = iterations
        
        # whether we choose to do the advanced version of the code
        if self.version == 'advanced':
            # add own defined batteries
            self.batteries = cluster_funct(self.houses)

            # ! change the model to the Smartgrid model
            for battery in self.batteries:
                battery.model = self
        else:
            self.batteries: list[House] = self.add_objects(district,
                                                           'batteries')

        self.cables: list[Cable] = []

        # the district which is chosen
        self.district = district

        # variable for representation
        self.information: list[dict[str, Any]] = []

        # create the grid
        self.create_grid()

        # order placement
        self.placement_order()

        # link houses
        self.link_houses()

        if version != "1":
            # create copied model
            self.copied_model: mesa.Model = copy.deepcopy(self)

            # lay the cables
            self.lay_cables_v2(self.batteries)

            # optimize connections
            self.optimization(iterations)
        else:
            # lay cables via version 1
            self.lay_cables_v1()

        # get representation info
        self.get_information()

    def bound(self) -> Tuple[int, int]:
        """
        This function generates the boundaries of the grid

        Returns:
            tuple[int, int]: the maximum x and y values for the grid
        """

        # find the maximum x and y values of the houses and battery lists
        max_x: int = max([max(self.houses, key=attrgetter('x'))] +
                    [max(self.batteries, key=attrgetter('x'))],
                    key=attrgetter('x'))
        max_y: int = max([max(self.houses, key=attrgetter('y'))] +
                    [max(self.batteries, key=attrgetter('y'))],
                    key=attrgetter('y'))

        return (max_x.x, max_y.y)

    def create_grid(self) -> None:
        width, height = self.bound()
        self.grid: mesa.space = mesa.space.MultiGrid(width + 1,
                                                     height + 1, False)

        # add houses to grid
        for house in self.houses:
            self.grid.place_agent(house, (house.x, house.y))

        # add batteries to grid
        for battery in self.batteries:
            self.grid.place_agent(battery, (battery.x, battery.y))

    def placement_order(self) -> None:
        """
        This function finds the order in which the houses get
        their battery assigned and sort the house list
        """

        for house in self.houses:
            # list of distances to all the batteries
            dist_batteries: list[int] = []

            # find the distance for all the batteries
            for battery in self.batteries:
                # add distance to list
                dist_batteries.append(house.distance(battery))

            # sort the list in ascending order
            dist_batteries.sort()

            # assign priority value to house
            house.priority = dist_batteries[4] - dist_batteries[0]

        # * sort houses based on priority
        self.houses.sort(key=lambda x: x.priority, reverse=True)

    def link_houses(self) -> None:
        """
        This function finds the best battery for each house to connect to
        and connects them.
        """

        if self.version == 'simulated annealing':
            random.shuffle(self.houses)

        # all placed houses
        houses_placed: List[House] = []

        # find closest battery for every house
        for house in self.houses:
            # smallest distance to a battery
            min_dist: int = -1

            # boolean to check if the house can connect to a battery
            battery_found: bool = False

            if self.version != 'simulated annealing':
                # check for all batteries
                for battery in self.batteries:
                    # distance to battery
                    dist: int = house.distance(battery)

                    # if a connection can be made, remember that
                    if min_dist == -1 and house.check_connection(battery):
                        min_dist = dist
                        best_battery: Battery = battery
                        battery_found = True
                    # update if distance to new battery is smaller than minimum
                    elif (min_dist > dist and
                          house.check_connection(battery)):
                        min_dist = dist
                        best_battery: Battery = battery
                        battery_found = True
            else:
                # pick a random battery order as destinations
                destinations: List[Battery] = random.sample(self.batteries,
                                             len(self.batteries))

                # check each battery if suitable
                for destination in destinations:
                    # if the battery has enough space connect and break
                    if house.check_connection(destination):
                        destination.add_house(house)
                        houses_placed.append(house)
                        break

            # add house to houses_placed if a battery is found
            if battery_found:
                # add house to battery and copy all the paths in battery
                best_battery.add_house(house)
                houses_placed.append(house)

        # get all the houses which are not placed
        houses_not_placed = [house for house in
                             self.houses if house not in houses_placed]

        # * shuffle houses such that unconnected houses are placed
        if len(houses_not_placed) > 0:
            distribute(self.batteries, houses_not_placed)

        # * copy all paths of the battery to initialize if not version 1
        if self.version != "1":
            for battery in self.batteries:
                battery.copy_all_paths()

    def lay_cables_v1(self) -> None:
        """
        This functions places the cables to connect all houses to the
        batteries without connecting to houses
        """

        # * initiate number of created cables
        self.num_cables = 0

        # initiate cable id's
        cable_id = 1000

        for house in self.houses:
            # x and y coordinate of the connected battery
            battery = house.connection

            # create a path from the house to the battery
            if battery.x >= house.x and battery.y <= house.y:
                horizontal = [(i, house.y) for i in
                              range(house.x, battery.x + 1, 1)]
                vertical = [(battery.x, i) for i in
                            np.arange(house.y, battery.y - 1, -1)]
            elif battery.x >= house.x and battery.y >= house.y:
                horizontal = [(i, house.y) for i in
                              range(house.x, battery.x + 1, 1)]
                vertical = [(battery.x, i) for i in
                            range(house.y, battery.y + 1, 1)]
            elif battery.x <= house.x and battery.y >= house.y:
                horizontal = [(i, house.y) for i in
                              np.arange(house.x, battery.x - 1, -1)]
                vertical = [(battery.x, i) for i in
                            range(house.y, battery.y + 1, 1)]
            elif battery.x <= house.x and battery.y <= house.y:
                horizontal = [(i, house.y) for i in
                              np.arange(house.x, battery.x - 1, -1)]
                vertical = [(battery.x, i) for i in
                            np.arange(house.y, battery.y - 1, -1)]

            path = horizontal + vertical

            # remove the duplicate coordinates at turns
            path = pd.unique(path).tolist()

            # add cables in grid
            for space in path:
                # add cable to the house and place it
                self.add_cable(space[0], space[1], house, cable_id)
                cable_id += 1

    def add_cable(self, x: int, y: int, house: House, cable_id: int) -> None:
        """
        Function that creates a cable at coordinates (x, y) and connects it to
        the specified house. Also gives the cable an unique id.

        Args:
            x (int): x coordinate of the cable.
            y (int): y coordinate of the cable.
            house (House): house for the cable to belong to.
            cable_id (int): unique id of the cable
        """

        # creates the cable
        new_cable = Cable(cable_id, self, x, y, house.connection.unique_id)
        new_cable.battery_connection = house.connection
        house.add_cable(new_cable)

        # update number of cables
        self.num_cables += 1

        # place cable in the grid
        self.grid.place_agent(new_cable, (x, y))

    def lay_cables_v2(self, battery_list: list[Battery]) -> None:
        """
        This functions places the cables to connect all houses to the
        batteries
        """

        # * initiate global variable for the number of cables
        self.num_cables: int = 0

        # places all cables for all the houses on the batteries
        for battery in self.batteries:
            # keep mergen paths until 1 remains
            while battery.get_len_paths() > 1:
                create_merged_path(battery)

            # if all paths are connected, draw all the cables
            self.num_cables += battery.lay_cables()

    def copy_optimize(self) -> None:
        """
        This function replaces self attributes with
        copied_model attributes when called
        """

        self.houses = self.copied_model.houses
        self.cables = self.copied_model.cables
        self.batteries = self.copied_model.batteries
        self.num_cables = self.copied_model.num_cables
        self.grid = self.copied_model.grid

    def optimization(self, iteration: int) -> None:
        """
        This function optimizes the battery allocations
        """

        optimization(self, iteration)

    def costs(self) -> int:
        """
        This function calculates the total costs for the cables and batteries

        Returns:
            int: total costs
        """

        # calculate cable costs
        cable_cost: int = self.num_cables * 9

        # calculate battery costs
        battery_cost: int = 0
        for battery in self.batteries:
            battery_cost += battery.costs

        return cable_cost + battery_cost

    def get_information(self) -> None:
        """
        This function creates the representation of the data
        """

        # dictionary for general information
        dct: dict[str, Any] = {}
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
                dct_house: dict[str, Any] = {}
                dct_house["location"] = str(house.x) + "," + str(house.y)
                dct_house["output"] = house.energy
                dct_house["cables"] = []

                # add location of all cables connected to houses
                # in the dictionary of information houses
                for cable in house.cables:
                    dct_house["cables"].append(str(cable.x)
                                               + "," + str(cable.y))
                dct["houses"].append(dct_house)

            # add all information to self.information
            self.information.append(dct)

    def add_objects(self, district: int,
                    info: str) -> Union[List[House], List[Battery]]:
        """
        Add houses or battery list of district depending on 'info'

        Args:
            district (int): district number
            info (str): 'houses' or 'batteries'

        Returns:
            Union[list[House], list[Battery]]:
                    a list with all the houses or batteries
        """

        # path to data
        path = '../Huizen&Batterijen/district_' + str(district) + '/district-' + str(district) + '_' + info + '.csv'

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
                    lst.append(Battery(count, self, x, y, energy, 5000))

                count += 1

        return lst


if __name__ == "__main__":
    # asks for valid district
    district = input("Which district would you like to simulate? (1-3): ")
    while district not in ["1", "2", "3"]:
        district = input("Which district would you like to simulate? (1-3): ")

    # convert district to integer
    district = int(district)

    # ask for valid version
    print("Which version would you like to run?", end=" ")
    version = input("(1/2/advanced/simulated annealing): ")
    while version not in ["1", "2", "advanced", "simulated annealing"]:
        print("Which version would you like to run?", end=" ")
        version = input("(1/2/advanced/simulated annealing): ")

    # asks for valid amount of iterations if not first version
    print("How many optimization iterations would you", end=" ")
    iterations = int(input("like to have (not useful for version 1): "))
    while iterations < 0:
        print("How many optimization iterations would you", end=" ")
        iterations = int(input("like to have (not useful for version 1): "))

    # run smartgrid and print the costs
    smartgrid = SmartGrid(district, version, iterations)
    print(smartgrid.costs())

    # export smartgrid information
    with open(f"../Smartgrid_data/smartgrid{district}_{version}.json",
              "w") as outfile:
        json.dump(smartgrid.information, outfile)

    if version == 'simulated annealing':
        plot_annealing()

    # asks for valid input request visualisation
    vis = input('Do you want a visualisation (Y/N): ')
    while vis not in ['Y', 'N']:
        vis = input('Do you want a visualisation (Y/N): ')

    if vis == 'Y':
        visualisation(smartgrid, SmartGrid)
