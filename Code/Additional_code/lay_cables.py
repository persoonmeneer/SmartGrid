"""
This program places cables smart
"""

from Agents.battery import Battery
from typing import Tuple, List
import pandas as pd
import copy


def dist_points(point_1: Tuple[int, int], point_2: Tuple[int, int]) -> int:
    """
    This function calculates the Manhattan distance between 2 points

    Args:
        point_1 (tuple[int, int]): a point
        point_2 (tuple[int, int]): another point

    Returns:
        int: the manhattan distance between the points
    """

    return abs(point_1[0] - point_2[0]) + abs(point_1[1] - point_2[1])


def dist_paths(path_1: List[Tuple[int, int]],
               path_2: List[Tuple[int, int]]) -> Tuple[int,
                                                       Tuple[int, int],
                                                       Tuple[int, int]]:
    """
    This function calculates the shortest distance between 2 paths

    Args:
        path_1 (list[tuple[int, int]]): a path
        path_2 (list[tuple[int, int]]): another path

    Returns:
        int: shortest Manhattan distance between the paths
    """

    min_dist: int = -1

    for point_1 in path_1:
        for point_2 in path_2:
            dist: int = dist_points(point_1, point_2)

            # update data when new lowest distance is found
            if dist < min_dist or min_dist == -1:
                min_dist = dist
                best_point_1 = point_1
                best_point_2 = point_2

    return min_dist, best_point_1, best_point_2


def min_dist_paths(path: List[Tuple[int, int]], battery: Battery) -> int:
    """
    This function calculates the shortest distance between a path
    and the path in battery

    Args:
        path (list[tuple[int, int]]): a path
        battery (Battery): a battery

    Returns:
        int: shortest manhattan distance between path and the battery path
    """

    # initialize minimum distance
    min_dist: int = -1

    # find minimum distance between path and all other paths
    for other_path in battery.copy_paths:
        # mim distance between 2 paths
        dist, point_1, point_2 = dist_paths(other_path, path)

        # update minimum distance when new minimum is found
        if min_dist == -1 or dist < min_dist:
            min_dist = dist

    return min_dist


def get_path(point_1: Tuple[int, int],
             point_2: Tuple[int, int], info: bool) -> List[Tuple[int, int]]:
    """
    This function creates a path hor-ver or ver-hor depending on info

    Args:
        point_1 (tuple[int, int]): a point
        point_2 (tuple[int, int]): another point
        info (int): flag for which combination path

    Returns:
        list[tuple[int, int]]: a path
    """

    # determine smallest and biggest x and y values
    small_x, small_y = min(point_1[0], point_2[0]), min(point_1[1], point_2[1])
    big_x, big_y = max(point_1[0], point_2[0]), max(point_1[1], point_2[1])

    # create path
    if info:
        vertical = [(point_1[0], i) for i in range(small_y, big_y + 1)]
        horizonal = [(i, point_2[1]) for i in range(small_x, big_x + 1)]
        return list(pd.unique(vertical + horizonal))

    horizonal = [(i, point_1[1]) for i in range(small_x, big_x + 1)]
    vertical = [(point_2[0], i) for i in range(small_y, big_y + 1)]
    return list(pd.unique(vertical + horizonal))


def get_best_path(point_1: Tuple[int, int], point_2: Tuple[int, int],
                  battery: Battery) -> List[Tuple[int, int]]:
    """
    This function selects the best path out of the 2 options

    Args:
        point_1 (tuple[int, int]): a point
        point_2 (tuple[int, int]): another point
        battery (Battery): a battery

    Returns:
        list[tuple[int, int]]: the best path
    """

    # get both paths
    path_1 = get_path(point_1, point_2, True)
    path_2 = get_path(point_1, point_2, False)

    # if only 2 paths left, it doesn't matter which path we choose
    if battery.get_len_paths() <= 2:
        return path_1

    # calculate the distances of bothe cases
    dist_1 = min_dist_paths(path_1, battery)
    dist_2 = min_dist_paths(path_2, battery)

    # return the smallest distance
    if dist_1 < dist_2:
        return path_1
    return path_2


def merge_paths(battery: Battery, index_1: int, index_2: int,
                path: List[Tuple[int, int]]) -> None:
    """
    merges 3 paths to 1

    Args:
        battery (Battery): a battery
        index_1 (int): index of a path
        index_2 (int): index of another path
        path (List[Tuple[int, int]]): path between the 2 other paths
    """

    # combine both paths and remove duplicates
    battery.all_paths[index_2] += battery.all_paths[index_1] + path

    # delete the old path
    del battery.all_paths[index_1]

    # copy path
    battery.copy_paths = copy.deepcopy(battery.all_paths)


def create_merged_path(battery: Battery) -> None:
    """
    This function creates a merged path

    Args:
        battery (Battery): a battery
    """

    min_dist: int = -1

    for i, path_1 in enumerate(battery.all_paths):
        # stop at last path
        if i == battery.get_len_paths() - 1:
            break

        for not_j, path_2 in enumerate(battery.all_paths[i + 1:]):
            # index for second path in self.all_paths
            j: int = not_j + i + 1

            # find the indexes of closest points of 2 paths and the distance
            dist, point_1, point_2 = dist_paths(path_1, path_2)

            # update data if new minimum is found
            if min_dist == -1 or dist < min_dist:
                min_dist = dist
                index_1 = i
                index_2 = j
                best_point_1 = point_1
                best_point_2 = point_2

    # remove the chosen paths oout of the copy list
    battery.copy_paths.pop(index_2)
    battery.copy_paths.pop(index_1)

    # get best path between the found closest paths
    path = get_best_path(best_point_1, best_point_2, battery)

    # now connect the paths together
    merge_paths(battery, index_1, index_2, path)
