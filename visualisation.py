import mesa
from smartgrid2 import SmartGrid
from Agents.house import House
from Agents.cable import Cable
from Agents.battery import Battery


def agent_portrayal(agent):
    portrayal = {"Layer": 1,
    "r": 1,}

    if type(agent) == House:
        bla = agent.connection.unique_id % 5
        if bla == 0:
            portrayal["Color"] = "black"
        elif bla == 1:
            portrayal["Color"] = "green"
        elif bla == 2:
            portrayal["Color"] = "blue"
        elif bla == 3:
            portrayal["Color"] = "purple"
        elif bla == 4:
            portrayal["Color"] = "yellow"
        else:
            portrayal["Color"] = "black"
        portrayal["Shape"] = "circle"
        portrayal["Filled"] = "false"
        # portrayal["Color"] = "blue"

    if type(agent) == Battery:
        portrayal["Shape"] = "circle"
        portrayal["Filled"] = "true"
        portrayal["Color"] = "red"

    if type(agent) == Cable:
        bla = agent.battery_id % 5
        if bla == 0:
            portrayal["Color"] = "black"
        elif bla == 1:
            portrayal["Color"] = "green"
        elif bla == 2:
            portrayal["Color"] = "blue"
        elif bla == 3:
            portrayal["Color"] = "purple"
        elif bla == 4:
            portrayal["Color"] = "yellow"
        else:
            portrayal["Color"] = "black"
            
        portrayal["r"] = 0.5
        portrayal["Shape"] = "circle"
        portrayal["Filled"] = "true"
        # portrayal["Color"] = "black"
        portrayal["Layer"] = 0

    return portrayal

if __name__ == "__main__":
    grid = mesa.visualization.CanvasGrid(agent_portrayal, 51, 51, 510, 510)

    server = mesa.visualization.ModularServer(
    SmartGrid, [grid], "Smart Grid", {"district": 1}
    )
    server.port = 8521 # The default
    server.launch()