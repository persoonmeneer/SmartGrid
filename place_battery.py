"""
This file will have the function which will place batteries in the smartgrid
using density-based clustering
"""

from sklearn.cluster import DBSCAN
from Agents.battery import Battery
from Agents.house import House
from typing import List
import numpy as np


def cluster_funct(houses_list: List[House]) -> List[Battery]:
    """
    

    Args:
        houses_list (List[House]): _description_

    Returns:
        List[Battery]: list of placed batteries
    """
    house_coord: np.array = []
    for house in houses_list:
        house_coord = np.append(house_coord, [house.x, house.y])
        
    clustering = DBSCAN(eps=8, min_samples=2).fit(X)