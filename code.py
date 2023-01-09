# Thomas, Karel en Joris

from __future__ import annotations
import csv

class General:
    def __init__(self, x: int, y: int, energy: float) -> None:
        self.x = x  # x coordinate
        self.y = y  # y coordinate
        self.energy = energy  # energy level


class House(General):
    def __init__(self, x, y, energy) -> None:
        super().__init__(x, y, energy)
        
    def distance(self, other: Battery) -> float:
        return abs(self.x - other.x) + abs(self.y - other.y)
        
        
class Battery(General):
    def __init__(self, x, y, energy) -> None:
        super().__init__(x, y, energy)
        
    def connect(self, other: House) -> None:
        """Reduces the remaining energy in the battery

        Args:
            other (House): A House with energy
        """
        
        self.energy -= other.energy
        

class Experiment:
    def __init__(self, district: int) -> None:
        
        self.houses = self.add_objects(district, 'houses')
        self.batteries = self.add_objects(district, 'batteries')
        
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
                    line[0:1] = neat_data
                    line = list(map(float, line))
                    
                # information
                x = line[0]
                y = line[1]
                energy = line[2]
                
                # append a house or Battery
                if info == 'houses':
                    lst.append(House(x, y, energy))
                else:
                    lst.append(Battery(x, y, energy))
                    
        return lst
        
print(len(Experiment(1).add_objects(1, 'batteries')))