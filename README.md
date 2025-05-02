# MDP-based Traffic Simulation

Final project for Decision Making Under Uncertainty at CU Boulder Spring 2025

## Michael's Additions- What I have so far:  
This is a simulation of the traffic intersection which can be viewed by running the code. 
I decided to do this in Python as I find it easier to work with- I think this should be fine for the project but let me know if there is a major issue with 
using Python over Julia.

Run by doing: 
python main.py

It's a 5 lane intersection. For each direction, there is a left turn lane (the lane in the middle), a straight lane, and a right turn lane (both to the right of the
left turn lane). Additionally, there is two more lanes for the opposite direction of travel. 

The traffic flow is currently random, but it would be interesting to add another traffic flow that changes with the timestep (to replicate rush hour traffic).
The speeds of the cars probably needs to be changed. 

If you run the file, it will just run a model that changes the traffic light on a fixed interval - this can be our baseline to beat. 
If you uncomment some of the code in main.main(), you will see the neural network that is designed to control the traffic lights. 
This needs major tuning - I'll continue to work on this. 

Another thing I added was collisions. I noticed in the simulations that the lights would change so fast it would cause the cars to crash, so I figure it's important
to include in the neural network as a heavy negative reward. If you run either model, you'll see the collisions printed out in chat when they occur. 

Everything should be working, but I'll have to look over the neural network with fresh eyes to see if there are no major errors with the logic inside it. 

## About the model

### The State Space

I think a good place to start for the state space is a vector of length N where
each entry in the vector represents the number of cars waiting for a given lane.

For example, consider the following example intersection:

![Intersection Diagram](IntersectionDiagram.jpg)

There is one lane to go each direction in the intersection, therefore the state space would be a vector of length 12, representing the number of cars that would be waiting at each position.

A heuristic we could use to identify these is the direction of origin, the direction of intended travel, and a unique ID, such as `:SW1` or `:NS2`. This will allow us to expand the number of lanes arbitrarily. For the time being, lets not consider combination lanes in which a driver could take one of many actions as is normally the case at intersections. Let us additionally ignore the complexity of U-turns.

Further states will likely be necessary to identify the current configuration of lights. This could on one hand be named instances of a light configuration in one state such as `NS+SN` or `NS+NE` (north to south straight and north to east left turn). On another hand, we could assign a boolean array of the length of states indicating whether traffic is allowed to flow. The later may be more space intensive, but could simplify how we do the generative transition model.

### The Action Space

The action space we want to keep small so that a tree search approach is efficient. The best way to do this appears to be selecting whether to keep the current light configuration or switch it to something new. There will be some sort of reward for keeping it as is to pass cars, but switching could just have a time penalty of some kind where the change of the light loses a cycle and you don't get the reward of passing cars. A slight deviation from this could be a situation where the left turn arrow can go off while still cashing in on an existing straight traffic reward.

Put simply: we want to identify valid changes to make from the existing state and have them available as actions.

### Transition Function

The transition function will be generative where we produce `s'` based on the action `a` selected and the current state `s`.

### Reward considerations

Simple formulation: reward based on the the number of cars passed. This is the overall throughput of the system. 

Something to be careful about here is the notion of starvation. If there are a lot of cars in one queue, they may be passed and cause long delays for cars in conflicting queues.

An expanded approach would be to consider the reward to be some combination of wait time relative to start position or decaying reward. For example, passing the first car in a queue has high reward and passing a later car is lower. We can play with this notion of decaying reward to prevent starvation. Maybe we take some inspiration from OS scheduling policies.

## Approach Considerations

Sunberg recommended tracking the time for each car. This would expand our state but be necessary if we want to branch into more complex reward heuristics.

The large state space shouldn't be a problem if we employ a tree search solution. Sunberg was giving the suggestion of sparse sampling tree search often, which makes me think it is a good initial approach to take up.

