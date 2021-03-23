import uuid
from agents import *
from order import *
from orderbook import *
from trade import *
from simulation import *
from tests import *
import multiprocessing

def runSimulation(name: str, num: int):
    print("Running simulation " + str(num))
    simulation = Simulation("runs/" + name + "/simulation.json")
    simulation.run()
    simulation.orderbooks["A"].write("runs/" + name + "/output" + str(num) + ".csv")
    print("Finished simulation " + str(num))

def main():
    name: str = "test"
    for i in range(100):
        p = multiprocessing.Process(target=runSimulation, args=(name, i,))
        p.start()

if __name__ == '__main__':
    main()