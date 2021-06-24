# High-Frequency Trading Financial Exchange Simulator

<br>This project is a discrete-event simulator for a financial exchange which takes latency into account. 
The simulatior is agent-based, with each trader being an agent acting with their given strategies based on information that the agent has received from the exchange.
Each agent can have a different latency function, which determines the time it takes information between the exchange and the agent.

<br>The simulator uses an event queue - events each have a time at which they are scheduled to happen, and the queue is sorted by each event's scheduled time.
Events are resolved in order of increasing time.

<br>Several types of traders and strategies are available. Check the "agents.py" file for more detailed explanations of each one.

## Setting up the project

<br>The simulator is written in Python 3.9. You'll need to have some libraries installed to run the code: pandas, numpy, matplotlib, random, heapq, multiprocessing, uuid, mpl_finance, json, and unittest.

## Running simulations

<br>This program is intended to simulate multiple simulations with identical parameters, and then to analyze the results of all these runs together.

<br>Each setup configuration for simulations is stored in a JSON file as "simulation.json".  
Some example configurations which you can run yourself are available in the "runs" folder. 
To see more information on how configurations work and what they mean, go to loadFile() method in "simulation.py" and fromJson() in "agent.py".
Feel free to experiment with running and editing the existing configurations, and with creating your own!

<br>Once you are ready to run your simulation setup, head over to "tester.py". 
Read the comment at the top of the file for more information on the input and output format of simulation runs.
Then, go to the main() method near the bottom and edit the line to reflect the configuration setup you want to run simulations for, and how many trial runs you want to run. Run the file when you are ready. Be warned - this may use up a large amount of your CPU's clock time and your RAM.

<br>Now that you have run your simulations and produced data points and statistics, you can analyze simulation data. Head over to "grapher.py" and scroll down to the bottom to find the main() function. 
You can set axis limits for the graphs to be produced if you want (there are already a few limits there, which you can comment out if you'd like to disable them).
Set the setup configuration's name in "simulationName" and how many simulations you ran in "simulationCount" and then run the file to produce graphs. 
It might take a while for all the graphs to generate, especially some graphs like "Net Worth".
The graphs will be saved in the same folder as the "simulation.json". 

<br>Now you can also analyze and display some additional overall stats for the simulations you just ran. 
While the graphs plot statistics over time, these stats reflect the simulation as a whole, on a per-agent basis.
Go to "tester.py" and edit the line in main() to reflect the simulations you want to view stats for.
Then, run the file. The results should be printed to the console.

## More

<br>This simulator was part of a greater project, which tried to determine the effects of Stale-Quote Arbitrage on markets. 
You can view the presentation of this project [https://www.youtube.com/watch?v=Q8meom3nWlU](here) (there are three projects in the video - this simulator relates to the first of those projects). 
You can also see the weekly blog for the project [https://siliconvalley.basisindependent.com/author/mateib/](here).

## Credits

<br>Matei Budiu
<br>
<br>Advisors:
<br>Matthew McCorkle (High School Teacher at BASIS Independent Silicon Valley)
<br>Ahmad Ghalayini (Graduate Student at Stanford University)