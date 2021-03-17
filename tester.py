import uuid
from agents import *
from order import *
from orderbook import *
from trade import *
from simulation import *
from tests import *

for i in range(100):
    print("Running simulation " + str(i))
    name: str = "test"
    simulation = Simulation("runs/" + name + "/simulation.json")
    simulation.run()

    simulation.orderbooks["A"].write("runs/" + name + "/output" + str(i) + ".csv")