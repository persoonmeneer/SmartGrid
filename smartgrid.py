# Thomas, Karel, Joris

from __future__ import annotations
import mesa
import random
from typing import Union
import csv
from operator import attrgetter


class House(mesa.Agent):
    def __init__(self, unique_id: int, model: mesa.model,
                 x: int, y: int, energy: float) -> None:
        super().__init__(unique_id, model)
        self.x = x  # x coordinate
        self.y = y  # y coordinate
        self.energy = energy  # energy level
        self.connection: Optional[battery] = None
        self.cables: list[Cables] = []
        self.priority: float = 0 # distance between 2 closest batteries

    def distance(self, other: Battery) -> float:
        return abs(self.x - other.x) + abs(self.y - other.y)

    def connect(self, other: House) -> None:
        """
        Reduces the remaining energy in the battery

        Args:
            other (House): A House with energy
        """

        other.energy -= self.energy

    def check_connection(self, other: Battery) -> bool:
        if other.energy - self.energy >= 0:
            return True
        return False


class Battery(mesa.Agent):
    def __init__(self, unique_id: int, model: mesa.model,
                 x: int, y: int, energy: float) -> None:
        super().__init__(unique_id, model)
        self.x = x  # x coordinate
        self.y = y  # y coordinate
        self.energy = energy  # energy level
        self.houses: list[Houses] = []

class Cable(mesa.Agent):
    def __init__(self, unique_id: int, model: mesa.Model,
                 x: int, y: int) -> None:
        super().__init__(unique_id, model)
        self.x = x  # x coordinate
        self.y = y  # y coordinate
        self.battery_connection: Optional[Battery] = None   


class SmartGrid(mesa.Model):
    def __init__(self, district: int) -> None:
        # objects
        self.houses: list[House] = self.add_objects(district, 'houses')
        self.batteries: list[House] = self.add_objects(district, 'batteries')
        
        # total numher of cable
        self.num_cables = 0

        width, height = self.bound()
        self.grid: mesa.space = mesa.space.MultiGrid(width + 1, height + 1, False)

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


    def bound(self) -> tuple[int, int]:
        """
        This function generates the boundaries of the grid

        Returns:
            tuple[int, int]: the maximum x and y values for the grid
        """
        
        # find the maximum x and y values of the houses and battery lists
        max_x = max([max(self.houses, key=attrgetter('x'))] + [max(self.batteries, key=attrgetter('x'))], key=attrgetter('x'))
        max_y = max([max(self.houses, key=attrgetter('y'))] + [max(self.batteries, key=attrgetter('y'))], key=attrgetter('y'))

        return (max_x.x, max_y.y)


    def add_objects(self, district: int, info: str) -> Union[list[House], list[Battery]]:
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
            house.priority = dist_batteries[1] - dist_batteries[0]
        
        # sort houses based on priority
        self.houses.sort(key=lambda x: x.priority, reverse=True)
              
    def link_houses(self) -> None:
        """
        This function finds the two closest batteries with enough capacity
        for every house and assigns the house to that battery
        """
        
        # find closest battery for every house
        for house in self.houses:
            # smallest distance to a battery
            min_dist = -1
            for battery in self.batteries:
                # distance to battery
                dist = house.distance(battery)
                
                # if the first battery, make it the smallest distance and connect
                if min_dist == -1 and house.check_connection(battery):
                    min_dist = dist
                    house.connection = battery
                # if distance to new battery is smaller than minimum, update
                elif min_dist > dist and house.check_connection(battery):
                    min_dist = dist
                    house.connection = battery
            

    def lay_cable(self) -> None:
        """
        This function connects the houses with the batteries by placing cables
        """
        
        # unique id for cables
        cable_id = 1000
        
        # create and place the cables for every house
        for house in self.houses:
            # cable list per house
            cable_list = []
            
            # x and y coordinate of the connected battery
            to_x, to_y = house.connection.x, house.connection.y

            # order the x and y values s.t. the cables can be laid
            small_x, small_y = min([house.x, to_x]), min([house.y, to_y])
            big_x, big_y = max([house.x, to_x]), max([house.y, to_y])

            # place cables in the x range for the house's y value
            for loc in range(small_x, big_x + 1):
                # create cable at given location and add to list
                new_cable = Cable(cable_id, self, loc, house.y)
                cable_list.append(new_cable)
                
                # update number of cables
                self.num_cables += 1
                
                # place cable in the grid
                self.grid.place_agent(new_cable, (loc, house.y))
                
                # update cable id
                cable_id += 1
                
            # place cables in the y range for the batteries' x value
            for loc in range(small_y, big_y + 1):
                # create cable at given location and add to list
                new_cable = Cable(cable_id, self, to_x, loc)
                cable_list.append(new_cable)
                
                # update number of cables
                self.num_cables += 1
                
                # place cable in the grid
                self.grid.place_agent(new_cable, (to_x, loc))
                
                #  update cable id
                cable_id += 1

            # assign cable list to the house
            house.cables = cable_list

    def costs(self) -> int:
        """
        This function calculates the total costs for the cables and batteries

        Returns:
            int: total costs
        """
        
        cable_cost = self.num_cables * 9
        battery_cost = 5000 * len(self.batteries)
        
        return cable_cost + battery_cost

if __name__ == "__main__":
    test_wijk_1 = SmartGrid(1)
    print(test_wijk_1.costs())

    test_wijk_2 = SmartGrid(2)
    print(test_wijk_2.costs())

    test_wijk_3 = SmartGrid(3)
    print(test_wijk_3.costs())