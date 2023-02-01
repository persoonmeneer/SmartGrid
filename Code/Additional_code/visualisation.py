from Agents.battery import Battery
from Agents.house import House
from Agents.cable import Cable
import matplotlib.pyplot as plt
import pandas as pd
import mesa


def agent_portrayal(agent):
    """
    This function returns a portrayal for the agent
    """

    portrayal = {"Layer": 1, "r": 1,}

    # define portayal of houses
    if type(agent) == House:
       # color house depending on battery id
       battery_id = agent.connection.unique_id % 5

       if battery_id == 0:
           portrayal["Color"] = "black"
       elif battery_id == 1:
           portrayal["Color"] = "green"
       elif battery_id == 2:
           portrayal["Color"] = "blue"
       elif battery_id == 3:
           portrayal["Color"] = "purple"
       elif battery_id == 4:
           portrayal["Color"] = "orange"
       else:
           portrayal["Color"] = "black"

       portrayal["Shape"] = "circle"
       portrayal["Filled"] = "false"

    # define portayal of battery
    if type(agent) == Battery:
       portrayal["Shape"] = "circle"
       portrayal["Filled"] = "true"
       portrayal["Color"] = "red"

    # define portayal of cable
    if type(agent) == Cable:
       # color house depending on battery id
       battery_id = agent.battery_id % 5

       if battery_id == 0:
           portrayal["Color"] = "black"
       elif battery_id == 1:
           portrayal["Color"] = "green"
       elif battery_id == 2:
           portrayal["Color"] = "blue"
       elif battery_id == 3:
           portrayal["Color"] = "purple"
       elif battery_id == 4:
           portrayal["Color"] = "orange"
       else:
           portrayal["Color"] = "black"
          
       portrayal["r"] = 0.5
       portrayal["Shape"] = "circle"
       portrayal["Filled"] = "true"
       portrayal["Layer"] = 0

    return portrayal

def plot_annealing():
    """
    This function plots the simulated annealing data
    """
    data = pd.read_csv("simulated_annealing_data.csv")
    
    plt.plot(list(range(len(data))), data.Costs)
    plt.show()
    print(data.Costs)
    
def visualisation(smartgrid, Model) -> None:
        grid = mesa.visualization.CanvasGrid(agent_portrayal, 51, 51, 510, 510)
        server = mesa.visualization.ModularServer(
        Model, [grid], "Smart Grid", {"district": smartgrid.district, "version": smartgrid.version, "iterations": smartgrid.iterations}
        )
        server.model = smartgrid
        server.port = 8521 # The default
        server.launch()
