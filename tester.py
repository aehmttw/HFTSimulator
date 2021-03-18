import uuid
from agents import *
from order import *
from orderbook import *
from trade import *
from simulation import *
from tests import *
from multiprocessing import Process

name: str = "testmultithread"

def runSimulation(num: int):
    print("Running simulation " + str(num))
    simulation = Simulation("runs/" + name + "/simulation.json")
    simulation.run()
    simulation.orderbooks["A"].write("runs/" + name + "/output" + str(num) + ".csv")

for i in range(100):
    p = Process(target=runSimulation, args=(i,))
    p.start()
    