 # Thomas, Karel, Joris
 
from __future__ import annotations
import mesa
from typing import Union, Optional, Any, Tuple, List
import csv
from operator import attrgetter
from Agents.battery import Battery
from Agents.house import House
import json
import copy
from lay_cables import *
import random
from simulated_annealing import optimization
from distribute import distribute
import matplotlib.pyplot as plt
  
class SmartGrid(mesa.Model):
    def __init__(self, district: int) -> None:
        # objects
        self.houses: list[House] = self.add_objects(district, 'houses')
        self.batteries: list[House] = self.add_objects(district, 'batteries')
        self.cables: list[Cable] = []
        
        # the district which is chosen
        self.district = district
        
        # variable for representation
        self.information: list[dict[str, Any]] = []
 
        # create the grid
        self.create_grid()

        # link houses
        self.link_houses()
        
        # create copied model
        self.copied_model = copy.deepcopy(self)
        
        # lay the cables
        self.lay_cables(self.batteries)
        
        # optimize connections
        self.optimization(100000)
       
        # get representation info
        self.get_information()   
 
    def bound(self) -> Tuple[int, int]:
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
    
    def create_grid(self) -> None:
        width, height = self.bound()
        self.grid: mesa.space = mesa.space.MultiGrid(width + 1,
                                                     height + 1, False)
        
        # add houses and batteries to grid
        for house in self.houses:
            self.grid.place_agent(house, (house.x, house.y))
 
        for battery in self.batteries:
            self.grid.place_agent(battery, (battery.x, battery.y))
 
    def link_houses(self) -> None:
        """
        This function finds a random battery for each house and connects them.
        If it can't connect all houses it tries all over.
        """
    
        random.shuffle(self.houses)
        
        houses_placed = []
        for house in self.houses:
            # pick a random battery order as destinations
            destinations = random.sample(self.batteries, len(self.batteries))

            # check each battery if suitable
            for destination in destinations:
                # if the battery has enough space connect and break
                if house.check_connection(destination):
                    destination.add_house(house)
                    houses_placed.append(house)
                    break
        
        # get all the houses which are not placed
        houses_not_placed = [house for house in self.houses if house not in houses_placed]
        
        # * shuffle houses such that unconnected houses are placed
        if len(houses_not_placed) > 0:
            distribute(self.batteries, houses_not_placed)
            
        # * copy all paths of the battery to initialize
        for battery in self.batteries:
            battery.copy_all_paths()

        print("*********************************************************************")
    def lay_cables(self, battery_list: List[Battery]) -> None:
        """
        This functions places the cables to connect all houses to the
        batteries
        """
        
        # * initiate global variable for the number of cables
        self.num_cables = 0
        
        # places all cables for all the houses on the batteries
        for battery in battery_list:
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
 
        cable_cost = self.num_cables * 9
        battery_cost = 5000 * len(self.batteries)
 
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
                    dct_house["cables"].append(str(cable.x) + "," + str(cable.y))
                dct["houses"].append(dct_house)
           
            # add all information to self.information
            self.information.append(dct)
       
    def add_objects(self, district: int, info: str) -> Union[List[House], List[Battery]]:
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
    
def plot_annealing():
    data = pd.read_csv("simulated_annealing_data.csv")
    
    plt.plot(list(range(len(data))), data.Costs)
    plt.show()

 
if __name__ == "__main__":
    test_wijk_1 = SmartGrid(1)
    print(test_wijk_1.costs())
    with open("district1.json", "w") as outfile:
        json.dump(test_wijk_1.information, outfile)
 
    plot_annealing()
    
    # test_wijk_2 = SmartGrid(2)
    # print(test_wijk_2.costs())
    # with open("district2.json", "w") as outfile:
    #     json.dump(test_wijk_2.information, outfile)
 
    # test_wijk_3 = SmartGrid(3)
    # print(test_wijk_3.costs())
    # with open("district3.json", "w") as outfile:
    #     json.dump(test_wijk_3.information, outfile)