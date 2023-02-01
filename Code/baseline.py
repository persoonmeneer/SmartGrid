"""
This program runs the baselines
"""

from __future__ import annotations
from Agents.cable import Cable
from Agents.house import House
from Agents.battery import Battery
from typing import Union, Optional, Tuple, List
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import mesa
import random
import csv


class SmartGrid(mesa.Model):
    """A smartgrid situation"""
    def __init__(self, district: int, version: int) -> None:
        # objects
        self.houses: List[House] = self.add_objects(district, 'houses')
        self.batteries: List[House] = self.add_objects(district, 'batteries')
        self.objects = self.houses + self.batteries

        self.num_cables: int = 0  # initialize at 0
        self.success: bool = True  # tracks the random composition
        self.costs_grid: int = 0  # initialize at 0

        # create grid space
        width, height = self.bound()
        self.grid = mesa.space.MultiGrid(width + 1, height + 1, False)

        # add houses to grid
        for i in self.houses:
            self.grid.place_agent(i, (i.x, i.y))

        # add batteries to grid
        for i in self.batteries:
            self.grid.place_agent(i, (i.x, i.y))

        # add cables to grid
        self.lay_cable_random()

    def bound(self) -> Tuple[int, int]:
        """
        This function finds the borders of the objects coordinates
        and returns these
        """

        x: int = 0
        y: int = 0

        for i in self.objects:
            if i.x > x:
                x = i.x
            if i.y > y:
                y = i.y

        return (x, y)

    def add_objects(self, district: int,
                    info: str) -> Union[List[House], List[Battery]]:
        """
        Add houses or battery list of district depending on 'info'

        Args:
            district (int): district number
            info (str): 'houses' or 'batteries'

        Returns:
            a list with all the houses or batteries
        """

        # path to data
        path = 'Huizen&Batterijen/district_' + str(district)
        path += '/district-' + str(district) + '_' + info + '.csv'

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

    def lay_cable_random(self) -> None:
        """
        This function creates random cables
        """

        cable_id: int = 1000

        random.shuffle(self.houses)

        for house in self.houses:
            # pick a random battery as destination
            destination = random.choice(range(len(self.batteries)))

            counter: int = 0
            # if the battery is not available pick a new one
            while not house.check_connection(self.batteries[destination]):
                counter += 1
                # if the house can't connect to any battery stop
                if counter == len(self.batteries):
                    self.success = False
                    return None

                destination += 1
                if destination > len(self.batteries) - 1:
                    destination = 0

            # connect the house to the random destination battery
            destination = self.batteries[destination]
            destination.add_house(house)

            # x and y coordinate of the connected battery
            battery = house.connection

            # create a path from the house to the battery
            if battery.x >= house.x and battery.y <= house.y:
                horizontal = [(i, house.y) for i in
                              range(house.x, battery.x + 1, 1)]
                vertical = [(battery.x, int(i)) for i in
                            np.arange(house.y, battery.y - 1, -1)]
            elif battery.x >= house.x and battery.y >= house.y:
                horizontal = [(i, house.y) for i in
                              range(house.x, battery.x + 1, 1)]
                vertical = [(battery.x, i) for i in
                            range(house.y, battery.y + 1, 1)]
            elif battery.x <= house.x and battery.y >= house.y:
                horizontal = [(int(i), house.y) for i in
                              np.arange(house.x, battery.x - 1, -1)]
                vertical = [(battery.x, i) for i in
                            range(house.y, battery.y + 1, 1)]
            elif battery.x <= house.x and battery.y <= house.y:
                horizontal = [(int(i), house.y) for i in
                              np.arange(house.x, battery.x - 1, -1)]
                vertical = [(battery.x, int(i)) for i in
                            np.arange(house.y, battery.y - 1, -1)]

            path = horizontal + vertical

            # remove the duplicate coordinates at turns
            path = pd.unique(path).tolist()

            if version == 1:
                for space in path:
                    # add cable to the house and place it
                    self.add_cable(space[0], space[1], house, cable_id)
                    cable_id += 1
            else:
                break_loop: bool = False
                first: bool = True
                for space in path:
                    if not first:
                        # check if a cable exists going to the battery
                        items = self.grid[space[0]][space[1]]

                        if len(items) >= 1:
                            for item in items:
                                # stop if cable goes to battery
                                if (isinstance(item, Cable) and
                                   item.battery_connection == house.connection):
                                    break_loop = True
                                    break

                            # break the loop
                            if break_loop:
                                break

                    # add cable to the house and place it
                    self.add_cable(space[0], space[1], house, cable_id)
                    cable_id += 1

                    first = False

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

    def costs(self) -> Optional[int]:
        """
        Function that calculates the costs of the random SmartGrid
        composition. If a house was unable to connect to any battery
        the function will return None.

        Returns:
            Optional[int]: an integer if all houses were connected else None.
        """

        # if not all batteries were connected return None
        if not self.success:
            return None

        # else calculate and return the costs
        cable_cost = self.num_cables * 9
        battery_cost = 5000 * len(self.batteries)
        self.costs_grid = cable_cost + battery_cost

        return self.costs_grid


if __name__ == "__main__":
    # information to keep track of
    results: List[int] = []
    fails: int = 0

    # asks user for valid input district
    district = input('Which district would you like to run (1-3): ')
    while district not in ["1", "2", "3"]:
        district = input('Which district would you like to run (1-3): ')

    # convert district to an integer
    district = int(district)

    # asks user for valid input version
    version = input('Which version would you like to run (1/2): ')
    while version not in ["1", "2"]:
        version = input('Which version would you like to run (1/2): ')

    # convert version to integer
    version = int(version)

    # run the random model x times and save the results
    iterations = int(input("How many iterations would you like to run: "))
    while iterations < 0:
        # run the random model x times and save the results
        iterations = int(input("How many iterations would you like to run: "))

    # run the simulation iterations times
    for i in range(iterations):
        test_wijk_1 = SmartGrid(1, version)

        # keep track of costs and number of fails
        if test_wijk_1.costs() is not None:
            results.append(test_wijk_1.costs())
        else:
            fails += 1

    # calculate percantage failed simulations and print that
    perc_fails = (fails / iterations) * 100
    print(f"The percentage failed is {round(perc_fails, 1)}%")

    # plot the distribution of the results
    plt.hist(results, bins=20)
    plt.show()

    # add the percentage of failure to the data and export
    results.append(perc_fails)
    df = pd.DataFrame(results, columns=["Costs"])
    df.to_csv(f"Baseline_data/baseline{district}_{version}.csv")
