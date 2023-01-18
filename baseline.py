# Thomas, Karel, Joris

from __future__ import annotations
import mesa
import random
from Agents.cable import Cable
from Agents.house import House
from Agents.battery import Battery
from typing import Union, Optional
import csv
import matplotlib.pyplot as plt
import copy
import pandas as pd


class SmartGrid(mesa.Model):
    def __init__(self, district):
        self.houses = self.add_objects(district, 'houses')
        self.batteries = self.add_objects(district, 'batteries')
        self.objects = self.houses + self.batteries
        self.num_cables = 0
        self.success = True
        self.costs_grid = 0

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
        cable_id = 1000
        
        random.shuffle(self.houses)
        
        for house in self.houses:
            # pick a random battery as destination
            destination = random.choice(range(len(self.batteries)))

            counter = 0
            # if the battery is not available pick a new one
            while not house.check_connection(self.batteries[destination]):
                counter += 1
                if counter == len(self.batteries):
                    self.success = False
                    return
                
                destination += 1
                if destination > len(self.batteries) - 1:
                    destination = 0

            destination = self.batteries[destination]
            house.connect(destination)
            
            # cable list per house
            cable_list = []

            # x and y coordinate of the connected battery
            battery = house.connection

            # order the x and y values s.t. the cables can be laid
            small_x, big_x = min([house.x, battery.x]), max([house.x, battery.x])
            small_y, big_y = min([house.y, battery.y]), max([house.y, battery.y])

            if house.y < battery.y:
                from_y, from_x = house.y, house.x
                to_x, to_y = battery.x, battery.y
            else:
                from_y, from_x = battery.y, battery.x
                to_x, to_y = house.x, house.y

            i = 0

    	    
            battery_block = True
            break_out_flag = False

            while battery_block == True:
                # no battery block found yet
                battery_block = False
                
                # make the path
                y1 = [(from_x, from_y + j) for j in range(i + 1)]
                x1 = [(j, from_y + i) for j in range(small_x, big_x + 1)]
                x2 = [(to_x, j) for j in range(from_y + i, to_y)]
                
                # remove the house and battery location
                if i > 0:
                    y1.pop(0)
                
                if len(x2) > 0:
                    x2.pop()

                # merge locations in one list
                cor_arr = y1 + x1 + x2
                # get all contents of the grid of the locations
                content = self.grid.get_cell_list_contents(cor_arr)
                
                # check if there is a different battery in path
                if any(isinstance(x, Battery) for x in content):
                        battery_block = True
                        i += 1

            for y in range(from_y, from_y + i):
                # add cable to the given house
                self.addCable(small_x, y, house, cable_id)
                # update cable id
                cable_id += 1

            for x in range(small_x, big_x + 1):
                # add cable to the given house
                self.addCable(x, small_y + i, house, cable_id)
                # update cable id
                cable_id += 1

            for y in range(from_y + i, to_y + 1):
                # add cable to the given house
                self.addCable(to_x, y, house, cable_id)
                # update cable id
                cable_id += 1

    def addCable(self, x, y, house, cable_id):
        new_cable = Cable(cable_id, self, x, y)
        house.addCable(new_cable)

        # update number of cables
        self.num_cables += 1

        # place cable in the grid
        self.grid.place_agent(new_cable, (x, y))
        
    def costs(self):
        if self.success == False:
            return None
        
        cable_cost = self.num_cables * 9
        battery_cost = 5000 * len(self.batteries)
        self.costs_grid = cable_cost + battery_cost
        return self.costs_grid
    

if __name__ == "__main__":
    results = []
    fails = 0
    
    runs = 100000
    for i in range(runs):
        test_wijk_1 = SmartGrid(1)
        if test_wijk_1.costs() != None:
            results.append(test_wijk_1.costs())
        else:
            fails += 1
    
    perc_fails = (fails / runs) * 100
    print(perc_fails)
    
    plt.hist(results, bins=20)
    plt.show()
    
    results.append(perc_fails)
    
    df = pd.DataFrame(results, columns = ["Costs"])
    
    
        
  
        
