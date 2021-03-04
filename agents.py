from orderbook import *
from order import *
from events import *
import random
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

    def fromJson(j, simulation: 'Simulation') -> 'Agent':
        name: str = j["name"]
        balance: float = j["balance"]
        
        type: str = j["type"]
        args: dict = j["typeargs"]

        shares: dict = j["shares"]

        agent: Agent = None
        if type == "basic":
            agent = BasicAgent(name, simulation, balance, shares, args)

        algtype: str = j["algorithm"]
        algargs: dict = j["algorithmargs"]

        algorithm: Algorithm = None

        if algtype == "fixedprice":
            algorithm = AlgorithmFixedPrice(agent, algargs)
        if algtype == "randomnormal":
            algorithm = AlgorithmRandomNormal(agent, algargs)

        agent.algorithm = algorithm

        latency: LatencyFunction = None
        lattype: str = j["latency"]
        latargs: str = j["latencyargs"]

        if lattype == "linear":
            latency = LatencyFunctionLinear(agent, latargs)
        elif lattype == "normal":
            latency = LatencyFunctionNormal(agent, latargs)

        agent.latencyFunction = latency

        return agent

    def inputData(self, trade: 'Trade', timestamp: float):
        raise NotImplementedError

class BasicAgent(Agent):
    def __init__(self, name: str, simulation: 'Simulation', balance: float, shares: dict, args: dict):
        super().__init__(name, simulation, balance, shares)

    def inputData(self, trade: 'Trade', timestamp: float):
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
    def getOrders(self, symbol: str, timestamp: float):
        raise NotImplementedError

class AlgorithmFixedPrice(Algorithm):
    # This class defines an algorithm that can be used by an agent 
    # args = price: float, quantity: int, buy: bool
    def __init__(self, agent: Agent, args: dict):
        super().__init__(agent)
        self.price = args["price"]
        self.quantity = args["quantity"]
        self.buy = args["buy"]

    # returns a list of orders to place
    def getOrders(self, symbol: str, timestamp: float):
        order = Order(self.agent, self.buy, symbol, self.quantity, self.price, timestamp)
        return [order]

class AlgorithmRandomNormal(Algorithm):
    # This class defines an algorithm that can be used by an agent 
    # args = price: float, quantity: int, buy: bool
    def __init__(self, agent: Agent, args: dict):
        super().__init__(agent)
        self.spread = args["spread"]
        self.quantity = args["quantity"]

    # returns a list of orders to place
    def getOrders(self, symbol: str, timestamp: float):
        price: float = self.agent.sharePrices[symbol]
        buy: bool = random.randint(1, 2) == 1
        order = Order(self.agent, buy, symbol, self.quantity, numpy.random.normal(price, self.spread * price), timestamp)
        return [order]
class LatencyFunction:
    # This class defines a latency distribution function that can be used by an agent
    def __init__(self, agent: Agent):
        self.agent = agent

    # returns a list of orders to place
    def getLatency(self) -> float:
        raise NotImplementedError

class LatencyFunctionLinear(LatencyFunction):
    # Linear latency function: latency is linearly between min and max parameters
    # args = min: float, max: float
    def __init__(self, agent: Agent, args: dict):
        super().__init__(agent)
        self.minLatency = args["min"]
        self.maxLatency = args["max"]

    def getLatency(self) -> float:
        return random.random() * (self.maxLatency - self.minLatency) + self.minLatency

class LatencyFunctionNormal(LatencyFunction):
    # Normal distribution latency function: latency follows a normal distribution with given mean and deviation
    # args = mean: float, deviation: float
    def __init__(self, agent: Agent, args: dict):
        super().__init__(agent)
        self.meanLatency = args["mean"]
        self.latencyDeviation = args["deviation"]

    def getLatency(self) -> float:
        return max(0, numpy.random.normal(self.meanLatency, self.latencyDeviation))

# todo - add multiple agent types

# one agent will use a simple algorithm
# another could be a market maker w/ historical data

# maybe explore some anomalies in the future with algorithms