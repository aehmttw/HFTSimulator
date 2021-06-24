from agents import *
from order import *
from orderbook import *
from trade import *
from simulation import *
from tests import *
import multiprocessing

# File structure:
# All simulations and simulation data are stored in the /runs folder
# Each "setup" has its own folder, with a configuration file named "simulation.json" inside of it
# For example, a simulation called "testsimulation" would have its config file in /runs/testsimulation/simulation.json 
# When n simulations of a setup are run, their results are saved in CSV files.
# The CSV files starting with "output" save metrics as they change over time
# Those starting with "stats" save single value metrics from the whole simulation, after it has been finished

# Runs a simulation inside the "runs" folder, with the given name and run index
def runSimulation(name: str, num: int):
    print("Running simulation " + str(num))
    simulation = Simulation("runs/" + name + "/simulation.json")
    simulation.run()
    simulation.orderbooks["A"].calculateVolatility(20000)
    simulation.orderbooks["A"].write("runs/" + name + "/output" + str(num) + ".csv")
    simulation.orderbooks["A"].writeStats("runs/" + name + "/stats" + str(num) + ".csv")

    print("Finished simulation " + str(num))

# Runs multiple simulations of the same configuration in parallel
# This will use up your CPU and RAM quite intensely, especially if running large numbers of simulations
def runMultipleSimulations(name: str, count: int):
    for i in range(count):
        p = multiprocessing.Process(target=runSimulation, args=(name, i,))
        p.start()

def main():
    # Edit this line to specify which setup you want to run simulations for, and how many simulations to run
    runMultipleSimulations("3speedsqa", 100)
    # After running this, run the tester and grapher files to compile an analysis of the simulations' data

if __name__ == '__main__':
    main()