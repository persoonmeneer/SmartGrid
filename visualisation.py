import mesa
from smartgrid import House, Battery, Cable, SmartGrid


def agent_portrayal(agent):
    portrayal = {"Layer": 1,
        "r": 1,}

    if type(agent) == House:
        match agent.connection.unique_id % 5:
            case 0:
                portrayal["Color"] = "black"
            case 1:
                portrayal["Color"] = "green"
            case 2:
                portrayal["Color"] = "blue"
            case 3:
                portrayal["Color"] = "purple"
            case 4:
                portrayal["Color"] = "yellow"
            case _:
                portrayal["Color"] = "black"
        portrayal["Shape"] = "circle"
        portrayal["Filled"] = "false"
        # portrayal["Color"] = "blue"

    if type(agent) == Battery:
        portrayal["Shape"] = "circle"
        portrayal["Filled"] = "true"
        portrayal["Color"] = "red"

    if type(agent) == Cable:
        match agent.battery_id % 5:
            case 0:
                portrayal["Color"] = "black"
            case 1:
                portrayal["Color"] = "green"
            case 2:
                portrayal["Color"] = "blue"
            case 3:
                portrayal["Color"] = "purple"
            case 4:
                portrayal["Color"] = "yellow"
            case _:
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
    server.port = 8521  # The default
    server.launch()
