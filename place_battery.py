"""
This file will have the function which will place batteries in the smartgrid
using density-based clustering
"""

from sklearn.cluster import KMeans
from Agents.battery import Battery
from Agents.house import House
from typing import List, Final
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# ! data of the different batteries in format ([capacity], [costs])
BIG_BAT_DAT: Final = (1800, 1800)
MID_BAT_DAT: Final = (900, 1350)
LOW_BAT_DAT: Final = (450, 900)

def cluster_funct(houses_list: List[House]) -> List[Battery]:
    """
    This function makes clusters

    Args:
        houses_list (List[House]): _description_

    Returns:
        List[Battery]: list of placed batteries
    """
    
    # make a dataset with the house locations
    X = []
    for house in houses_list:
        X.append([house.x, house.y])
    
    # initialize highest total cluster output and number of clusters
    max_cluster_output = BIG_BAT_DAT[0] + 1
    num_clust = 1
    
    # convert to 2D numpy array
    X = np.array(X)
    
    while max_cluster_output > BIG_BAT_DAT[0]:  

        # run K-means on X
        clustering = KMeans(n_clusters=num_clust, random_state=0).fit(X)

        # create pandas dataframe with the data
        data = pd.DataFrame()
        data['x'] = [house.x for house in houses_list]
        data['y'] = [house.y for house in houses_list]
        data['output'] = [house.energy for house in houses_list]
        data['cluster'] = clustering.labels_
        
        # * stop while loop if all the cluesters are less then big battery capacity
        for i in data['cluster']:
            # filter the data by cluster
            filter_data = data[data.cluster == i]
            cluster_output = filter_data['output'].sum()
            
            # stop for loop when too high a cluster_output has been found
            if cluster_output >= BIG_BAT_DAT[0]:
                break
        else:
            break
        
        num_clust += 1