import mesa
from smartgrid2 import SmartGrid
from Agents.house import House
from Agents.cable import Cable
from Agents.battery import Battery


def agent_portrayal(agent):
    portrayal = {"Layer": 1,
        "r": 1,}

    if type(agent) == House:
        portrayal["Shape"] = "circle"
        portrayal["Filled"] = "true"
        portrayal["Color"] = "blue"

    if type(agent) == Battery:
        portrayal["Shape"] = "circle"
        portrayal["Filled"] = "true"
        portrayal["Color"] = "red"

    if type(agent) == Cable:
        portrayal["Shape"] = "circle"
        portrayal["Filled"] = "true"
        portrayal["Color"] = "black"
        portrayal["Layer"] = 0

    return portrayal

if __name__ == "__main__":
    grid = mesa.visualization.CanvasGrid(agent_portrayal, 51, 51, 510, 510)

    server = mesa.visualization.ModularServer(
        SmartGrid, [grid], "Smart Grid", {"district": 1}
    )
    server.port = 8521  # The default
    server.launch()
