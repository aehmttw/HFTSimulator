from orderbook import *
from order import *
from events import *
import random
import json
class Agent:
    def __init__(self, name: str, simulation: 'Simulation', balance: float, shares: dict):
        self.balance = balance
        self.name = name
        self.simulation = simulation
        
        # Symbol -> amount
        self.shares = shares

        self.orderBooks = dict()
        self.sharePrices = dict()

        self.algorithm = None
        self.latencyFunction = None

    def fromFile(file: str, simulation: 'Simulation'):
        with open(file) as f:
            sections = f.read().splitlines()

        name: str = sections[0]
        balance: float = float(sections[1])
        
        type: str = sections[2].split(":")[0]
        args: str = sections[2].split(":")[1]

        shares = dict()
        for s in sections[3].split(","):
            s1 = s.split("=")
            shares[s1[0]] = int(s1[1])

        agent: Agent = None
        if type == "basic":
            agent = BasicAgent(name, simulation, balance, shares, args)

        algtype: str = sections[4].split(":")[0]
        algargs: str = sections[4].split(":")[1]

        algorithm: Algorithm = None

        if algtype == "fixedprice":
            algorithm = AlgorithmFixedPrice(agent, algargs)

        agent.algorithm = algorithm

        latency: LatencyFunction = None
        lattype: str = sections[5].split(":")[0]
        latargs: str = sections[5].split(":")[1]

        if lattype == "linear":
            latency = LatencyFunctionLinear(agent, latargs)

        agent.latencyFunction = latency

        return agent

    def inputData(self, trade: 'Trade', timestamp: int):
        raise NotImplementedError

class BasicAgent(Agent):
    def __init__(self, name: str, simulation: 'Simulation', balance: float, shares: dict, args: str):
        super().__init__(name, simulation, balance, shares)

    def inputData(self, trade: 'Trade', timestamp: int):
        self.sharePrices[trade.symbol] = trade.price
        orders = self.algorithm.getOrders(trade.symbol, timestamp)

        for order in orders:
            self.simulation.pushEvent(EventOrder(timestamp + self.latencyFunction.getLatency(), order, self.simulation.orderbooks[trade.symbol]))

    
# market maker - could schedule events at for self
# maybe plot event queue size over time to see how long to simulate for, to see practicality

class Algorithm:
    # This class defines an algorithm that can be used by an agent 
    def __init__(self, agent: Agent):
        self.agent = agent

    # returns a list of orders to place
    def getOrders(self, symbol: str, timestamp: int):
        raise NotImplementedError

class AlgorithmFixedPrice(Algorithm):
    # This class defines an algorithm that can be used by an agent 
    # args = price: float, quantity: int, buy: bool
    def __init__(self, agent: Agent, args: str):
        super().__init__(agent)
        a = args.split(",")
        self.price = float(a[0])
        self.quantity = int(a[1])
        self.buy = a[2] == "True"
        print(a[2])

    # returns a list of orders to place
    def getOrders(self, symbol: str, timestamp: int):
        order = Order(self.agent, self.buy, symbol, self.quantity, self.price, timestamp)
        return [order]

class LatencyFunction:
    # This class defines a latency distribution function that can be used by an agent
    def __init__(self, agent: Agent):
        self.agent = agent

    # returns a list of orders to place
    def getLatency(self) -> int:
        raise NotImplementedError

class LatencyFunctionLinear(LatencyFunction):
    # Linear latency function: latency is linearly between min and max parameters
    # args = min: int, max: int
    def __init__(self, agent: Agent, args: str):
        super().__init__(agent)
        a = args.split(",")
        self.minLatency = int(a[0])
        self.maxLatency = int(a[1])

    def getLatency(self) -> int:
        return random.randint(self.minLatency, self.maxLatency)

# todo - add multiple agent types

# one agent will use a simple algorithm
# another could be a market maker w/ historical data

# maybe explore some anomalies in the future with algorithms