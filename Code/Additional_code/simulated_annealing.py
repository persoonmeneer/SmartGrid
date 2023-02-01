"""
This python file does simulated annealing with the geometric rule
"""

from typing import List
import pandas as pd
import copy
import random


def optimization(smartgrid, iteration: int) -> None:
    """
    This function optimizes the lay-out of the cables

    Args:
        smartgrid (Smartgrid): a smartgrid
        iteration (int): number of iterations
    """

    # initialise acceptance probability, minimum costs and best model
    acc_prob: float = 1
    min_costs: int = smartgrid.costs()
    best_model = copy.deepcopy(smartgrid)

    # list with the cost for each accepted iteration
    results: List[int] = [min_costs]

    # optimize for iteration number of iterations
    for i in range(iteration):
        # create copy of the model
        empty_model = copy.deepcopy(smartgrid.copied_model)

        # cost of current lay-out cables
        old_costs: int = smartgrid.costs()

        # select 2 different random batteries
        battery_1, battery_2 = random.sample(smartgrid.copied_model.batteries, 2)

        # select random house with lower priority
        house_1 = random.choice(battery_1.houses)
        house_2 = random.choice(battery_2.houses)

        # skip if not enough capacity in the batteries
        if (house_1.energy - house_2.energy > battery_2.energy or
           house_2.energy - house_1.energy > battery_1.energy):
            continue

        # remove connection of house with battery
        battery_1.remove_house(house_1)
        battery_2.remove_house(house_2)

        # add different house
        battery_1.add_house(house_2)
        battery_2.add_house(house_1)

        # changed_copy
        changed_empty_model = copy.deepcopy(smartgrid.copied_model)

        # create the cables
        smartgrid.copied_model.lay_cables_v2(smartgrid.copied_model.batteries)

        # calculate the new costs
        new_costs = smartgrid.copied_model.costs()

        # acceptance probability
        acc_prob *= 0.99

        # replace best model when lower cost has been found
        if new_costs < min_costs:
            best_model = smartgrid.copied_model
            min_costs = new_costs

        # do simulated annealing when necessary
        if (new_costs < old_costs and
           smartgrid.version != 'simulated annealing'):
            smartgrid.copy_optimize()
        elif (smartgrid.version == 'simulated annealing' and
              (new_costs < old_costs or random.random() <= acc_prob)):
            smartgrid.copy_optimize()
            results.append(new_costs)
            smartgrid.copied_model = changed_empty_model
            continue

        # make copied model empty again
        smartgrid.copied_model = empty_model

    # make the smartgrid the best selection of the iterated models
    smartgrid.copied_model = best_model
    smartgrid.copy_optimize()

    # export results when simulated annealing is done
    if smartgrid.version == 'simulated annealing':
        df = pd.DataFrame(results, columns=["Costs"])
        df.to_csv("Smartgrid_data/simulated_annealing_data.csv")
