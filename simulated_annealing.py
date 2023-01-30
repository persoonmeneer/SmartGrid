"""
This python file does simulated annealing with the geometric rule
"""

import copy
import random
from math import exp

def optimization(smartgrid, iteration: int) -> None:
    """
    This function optimizes the lay-out of the cables

    Args:
        smartgrid (Smartgrid): a smartgrid
        iteration (int): number of iterations
    """
    
    # initialise acceptance probability, minimum costs and best model
    acc_prob = 1
    min_costs = 40_000
    best_model = copy.deepcopy(smartgrid)
    
    # optimize for iteration number of iterations
    for i in range(iteration):
        # create copy of the model
        empty_model = copy.deepcopy(smartgrid.copied_model)
        
        # cost of current lay-out cables
        old_costs = smartgrid.costs()
        
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
        smartgrid.copied_model.lay_cables(smartgrid.copied_model.batteries)
        
        # calculate the new costs
        new_costs = smartgrid.copied_model.costs()
        
        # acceptance probability
        # acc_prob *= 0.99
        acc_prob = acc_prob / (1 + 0.1 * acc_prob)
        
        # if new lay-out has less costs or with certain probability accept change
        if new_costs < min_costs:
            best_model = smartgrid.copied_model
            min_costs = new_costs
            
        if new_costs < old_costs or random.random() <= acc_prob:
            smartgrid.copy_optimize()
            smartgrid.copied_model = changed_empty_model
        else:  
            smartgrid.copied_model = empty_model
    
    # make the smartgrid the best selection of the iterated models
    smartgrid.copied_model = best_model
    smartgrid.copy_optimize()
