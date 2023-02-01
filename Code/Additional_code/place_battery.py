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

# ! data of the different batteries in format ([capacity], [costs])
BIG_BAT_DAT: Final = (1800, 1800)
MID_BAT_DAT: Final = (900, 1350)
LOW_BAT_DAT: Final = (450, 900)


def check_point_in_df(houses_list: List[Battery], x: int, y: int) -> bool:
    """
    This function checks if (x, y) is in the dataframe

    Args:
        dataframe (pd.DataFrame): a dataframe with data houses
        x (int): x value in grid
        y (int): y value in grid

    Returns:
        bool: True if a house is placed at (x, y) else False
    """

    for house in houses_list:
        if house.x == x and house.y == y:
            return True

    return False


def cluster_funct(houses_list: List[House]) -> List[Battery]:
    """
    This function makes clusters

    Args:
        houses_list (List[House]): all houses

    Returns:
        List[Battery]: list of placed batteries
    """

    # initiate battery list
    battery_lst: List[Battery] = []

    # make a dataset with the house locations
    X = []
    for house in houses_list:
        X.append([house.x, house.y])

    # initialize highest total cluster output and number of clusters
    num_clust: int = 1

    # convert to 2D numpy array
    X = np.array(X)

    while True:
        # run K-means on X
        clustering = KMeans(n_clusters=num_clust, random_state=0).fit(X)

        # create pandas dataframe with the data
        data = pd.DataFrame()
        data['x'] = [house.x for house in houses_list]
        data['y'] = [house.y for house in houses_list]
        data['output'] = [house.energy for house in houses_list]
        data['cluster'] = clustering.labels_

        # * stop loop if all the clusters are less then big battery capacity
        for i in data['cluster']:
            # filter the data by cluster
            filter_data = data[data.cluster == i]
            cluster_output = filter_data['output'].sum()

            # stop for loop when too high a cluster_output has been found
            if cluster_output >= BIG_BAT_DAT[0]:
                break
        else:
            break

        # update number of clusters
        num_clust += 1

    # definte the unique clusters
    unique_clusters = data['cluster'].unique()

    # create sorted clusters by total output batteries
    for i in unique_clusters:
        # filter the data by cluster
        filter_data = data[data.cluster == i]

        # calculate the output sum
        cluster_output = filter_data['output'].sum()

        # calculate centre point
        centre_x = round(filter_data['x'].mean())
        centre_y = round(filter_data['y'].mean())

        # variable which checks if the centre points are in filter_data
        point_in_df: bool = check_point_in_df(houses_list, centre_x, centre_y)

        # check surrounding points if that is empty if so, edit centre points
        if point_in_df:
            # pass surrounding places
            for x in range(centre_x - 1, centre_x + 2):
                for y in range(centre_y - 1, centre_y + 2):
                    # check centre point
                    new_point_in_df = check_point_in_df(houses_list, x, y)
                    if not new_point_in_df:
                        centre_x, centre_y = x, y

        # edit cluster output when at last
        if i == unique_clusters[-1]:
            # house and battery energy levels
            house_output = sum([house.energy for house in houses_list])
            battery_capacity = sum([battery.capacity
                                    for battery in battery_lst])

            # modify cluster output
            cluster_output = house_output - battery_capacity

        # create batteries
        if cluster_output > MID_BAT_DAT[0]:
            battery_lst.append(Battery(i, i, centre_x, centre_y,
                                       BIG_BAT_DAT[0], BIG_BAT_DAT[1]))
        elif cluster_output > LOW_BAT_DAT[0]:
            battery_lst.append(Battery(i, i, centre_x, centre_y,
                                       MID_BAT_DAT[0], MID_BAT_DAT[1]))
        else:
            battery_lst.append(Battery(i, i, centre_x, centre_y,
                                       LOW_BAT_DAT[0], LOW_BAT_DAT[1]))

    return battery_lst
