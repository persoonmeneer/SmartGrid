# Thomas, Karel, Joris

from __future__ import annotations
import mesa
import random
from typing import Union
import csv
import matplotlib.pyplot as plt
import copy


class House(mesa.Agent):
    def __init__(self, unique_id, model, x, y, energy) -> None:
        super().__init__(unique_id, model)
        self.x = x  # x coordinate
        self.y = y  # y coordinate
        self.energy = energy  # energy level
        self.connection = None
        self.cables = []
        self.two_batteries = 0 # distance between 2 closest batteries

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
    def __init__(self, unique_id, model, x, y, energy) -> None:
        super().__init__(unique_id, model)
        self.x = x  # x coordinate
        self.y = y  # y coordinate
        self.energy = energy  # energy level
        self.houses = []

class Cable(mesa.Agent):
    def __init__(self, unique_id, model, x, y):
        super().__init__(unique_id, model)
        self.x = x  # x coordinate
        self.y = y  # y coordinate


class SmartGrid(mesa.Model):
    def __init__(self, district):
        self.houses = self.add_objects(district, 'houses')
        self.batteries = self.add_objects(district, 'batteries')
        self.objects = self.houses + self.batteries
        self.num_cables = 0
        self.success = True

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


    def bound(self):
        x = 0
        y = 0

        for i in self.objects:
            if i.x > x:
                x = i.x
            if i.y > y:
                y = i.y

        return (x, y)


    def add_objects(self, district: int, info: str) -> Union[list[House], list[Battery]]:
        """Add houses or battery list of district depending on 'info'

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

    def lay_cable_random(self):
        count = 1000
        
        random.shuffle(self.houses)
        
        for house in self.houses:
            i = 0
            lst = []
            destination = random.choice(range(len(self.batteries)))

            while not house.check_connection(self.batteries[destination]):
                i += 1
                if i == len(self.batteries):
                    self.success = False
                    return
                
                destination += 1
                if destination > len(self.batteries) - 1:
                    destination = 0

            destination = self.batteries[destination]
            house.connect(destination)
            
            to_x, to_y = destination.x, destination.y

            small_x, small_y = min([house.x, to_x]), min([house.y, to_y])
            big_x, big_y = max([house.x, to_x]), max([house.y, to_y])

            for loc in range(small_x, big_x + 1):
                count += 1
                a = Cable(count, self, loc, house.y)
                lst.append(a)
                self.num_cables += 1
                self.grid.place_agent(a, (loc, house.y))

            for loc in range(small_y, big_y + 1):
                count += 1
                a = Cable(count, self, to_x, loc)
                lst.append(a)
                self.num_cables += 1
                self.grid.place_agent(a, (to_x, loc))

            house.cables = lst

    def costs(self):
        if self.success == False:
            return None
        
        cable_cost = self.num_cables * 9
        battery_cost = 5000 * len(self.batteries)
        return cable_cost + battery_cost

if __name__ == "__main__":
    results = []
    fails = 0
    
    for i in range(10000):
        test_wijk_1 = SmartGrid(1)
        if test_wijk_1.costs() != None:
            results.append(test_wijk_1.costs())
        else:
            fails += 1
    
    perc_succes = (fails / 10000) * 100
    print(perc_succes)
    
    plt.hist(results, bins=20)
    plt.show()
        
