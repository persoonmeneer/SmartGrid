"""
This programs distributes all the houses s.t. all the houses
are connected to batteries
"""

from Agents.house import House
from Agents.battery import Battery
from typing import List


def distribute(batteries: List[Battery], houses: List[House]) -> None:
    """
    This function distributes house s.t. the remaining unconnected
    houses can be placed

    Args:
        batteries (List[Battery]): all batteries
        houses (List[House]): unconnected houses
    """

    for house in houses:
        house_added: bool = False

        # sort batteries by left over capacity
        batteries.sort(key=lambda x: x.energy, reverse=True)

        # batterie with highest energy will receive the house
        destination = batteries[0]

        # reverse list so that least priority houses are at the front
        destination.houses.reverse()

        for helper in batteries[1:]:
            # max energy helper battery can receive
            capacity = helper.energy

            # move a house from the destination to helper if enough capacity
            for switch in destination.houses[:10]:
                if switch.energy <= capacity:
                    destination.remove_house(switch)
                    helper.add_house(switch)

                    # if enough space in destination add the unplaced house
                    if destination.energy >= house.energy:
                        destination.houses.reverse()
                        destination.add_house(house)
                        house_added = True

        if house_added:
            continue

        # if the unplaced house is not added yet make more space
        for helper in batteries[1:]:
            # we will trade a house from helper and destination to make space
            while True:
                capacity = helper.energy
                # we only consider houses with low priority
                candidates_dest = destination.houses[:10]

                # reverse list so that least priority houses are at the front
                helper.houses.reverse()
                candidates_helper = helper.houses[:10]

                # the helper list can get a max netto increase of capacity
                biggest_change = 0

                for k in candidates_dest:
                    for z in candidates_helper:
                        change = k.energy - z.energy

                        if change > biggest_change and change < capacity:
                            best_dest = k
                            best_help = z
                            biggest_change = change

                # if a good change has been found make it
                if biggest_change > 0:
                    # disconnect both houses from their lists
                    destination.remove_house(best_dest)
                    helper.remove_house(best_help)

                    # reverse lists to reestablish priority
                    helper.houses.reverse()
                    destination.houses.reverse()

                    # add houses back to the opposite list
                    helper.add_house(best_dest)
                    destination.add_house(best_help)

                    # reverse the destination list
                    destination.houses.reverse()
                else:
                    break

            # add unplaced house to the destination battery when space
            if destination.energy >= house.energy:
                destination.houses.reverse()
                destination.add_house(house)
                house_added = True
                break
