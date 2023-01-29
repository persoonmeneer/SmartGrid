import copy
import random

def optimization(smartgrid, iteration: int) -> None:
    """
    This function optimizes the lay-out of the cables

    Args:
        smartgrid (_type_): a smartgrid
        iteration (int): number of iterations
    """
    
    # optimize for 10000 iterations
    for i in range(iteration):
        # create copy of the model
        copy_model = copy.deepcopy(smartgrid.copied_model)
        
        # cost of current lay-out cables
        costs = smartgrid.costs()
        
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
        
        # create the cables
        smartgrid.copied_model.lay_cables(smartgrid.copied_model.batteries)
        
        # if new lay-out has more costs, go back to old setup
        if smartgrid.copied_model.costs() >= costs:
            smartgrid.copied_model = copy_model
        else:
            smartgrid.copy_optimize()
            smartgrid.copied_model = copy_model