# SmartGrid

### Overview
In this SmartGrid problem we have houses with an energy output, batteries with a max capacity to contain this output and cables to connect the houses to the batteries. The energy company wants to connect every house to a battery with sufficient energy space. The problem however, is that cables and batteries cost money and we want to minimize spenditures.

In this project we try to find the best cost-effective solution to this problem. We want to use the least amount of batteries and cables but still make sure that every house has a battery with enough capacity to connect to. The question remains where to place the batteries, what house to connect to what battery and how to lay the cables. To answer this problem we used an agent based model and object oriented programming. This is helpful since this way each house, cable and battery is an agent which carries information about all the other objects it interacts with.


#### Smartgrid 1.0
To find a solution to this problem we started with a simpler problem. Namely, we have a district with batteries already set in place and each house has their own individual cable.  

The code that solves this exact problem can be ran using: 
```
python main.py
```
and giving as input smartgrid followed by a district, the version 1 and then specifying the amount of iterations. It uses a "distribute" algorithm which is a combination of a greedy and iterative algorithm that distributes the houses over the batteries. It does so by first determining which houses should be assigned to a battery first by calculating the difference between the distance of the furtherst battery and the closest battery. If this difference is large we prioritize this house.

Then following this priority rule we assign each house to the best available battery. All the houses that can not connect to a battery are placed in a seperate list and we switch random houses with low priority between batteries to make space. If enough space has been created a house is connected to the battery. Since the houses all have their own cable, it does not really matter how the cable is placed as long as it has the shortest Manhattan distance. That is why we have chosen that the cable is always laid in a right angle.


#### Smartgrid 2.0
In the 2.0 version of our problem we abandon the relaxation that each house has their own cable to the battery. Now we include that the cables of houses can merge if they go to the same battery and hence will have a reduction in costs. This adds the extra dimension that it might be better to connect to a cable instead of the battery directly.

The code that solves this exact problem can be ran using:
```
python main.py
```
and then giving the input smartgrid followed by a district, the version 2 and then specifying the amount of iterations. We use the same distribute algorithm to distribute the houses over the batteries. The difference is in the algorithm we use to lay the cables. For this, we look at all the houses connected to the battery and the battery itself, and the Manhattan distance between them. After this is done, we connect the two objects which are closest together which becomes a line created by cables. Then we look again at the Manhattan distance's, only now between the houses and batteries and the placed cables and do this until all houses and the battery are connected to eachother. Additionally, in case of an angle, the path which is created is determined by which of the two options has the next closest object to the line. The created line which minimises this is chosen.

To further optimize this solution we run a hillclimber algorithm on this composition. This is where we need the number of iterations for. We do this by switching two allegiable houses between two batteries and laying the cables again. Accepting changes that reduce costs leads us to climb deeper into our local minimum.

#### Simulated annealing
We also made a simulated annealing algorithm to find a minimum. Our simulated annealing algorithm has as starting position a random correct distribution of the houses over the batteries. every iteration we switch two allegiable houses between two batteries and lay the cables again. If this new composition has lower costs we always accept the change. If it is worse we accept it with a probability. For every iteration this probability is multiplied by 0.99. Using this algorithm we should be able to climb out of local minima and descend into the global minimum. This algorithm can be ran by using:
```
python main.py
```
and then giving the input smartgrid followed by a distrcit and then simulated annealing followed by the amount of iterations.
#### Advanced
Finally we also decide where the batteries can be placed in the district. Not only that but we decide what batteries to use since they are different in capacity and price. We used the algorithm K-means to solve this problem. This algorithm creates k specified clusters in a dataset. In our case we create clusters from the houses. We implemented K-means by increasing the number of clusters by 1 if the sum of output of any cluster exceeds the biggest battery's capacity. When we have created the clusters, we calculate the centre point of the clusters by finding the average of all houses' coordinates (rounded to closest integer) If there is no house there, a battery is placed which has enough capacity for the whole cluster. If there is a house there, the battery is placed next to the average coordinate which is empty. When we are at the last cluster which does not yet have a battery, the difference between the existing batteries remaining capacity and all houses is calculated, and a smallest battery that can store that is placed in the centre of the last cluster. Then we use the "distribute.py" algorithm mentioned before to distribute the houses over the batteries. Laying the cables follows the same algorithm as mentioned before.

#### Requirements
This codebase has been written completely in python. In requirements.txt are all the needed packages to run the code succesfully. They can be installed using the following:
```
pip install -r requirements.txt
```

## Usage
All the code can be ran using 
```
python main.py
```
This gives you first the option to run a baseline to see the distribution of random solutions without optimization or to run smartgrid which gives the option to run one of the specific algorithms above. Then you choose what district you want to use, what algorithm (except if you choose baseline) and then how many iterations. After that has run, you get the option to see the results of the simulation in case "smartgrid" has been chosen.

#### Authors
+ Karel Vreeburg
+ Thomas van Iperen
+ Joris Van Der Mije