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
     
    def inputData(self, trade: 'Trade', timestamp: int):
        self.sharePrices[trade.symbol] = trade.price
        orders = self.algorithm.getOrders(trade.symbol, timestamp)

        for order in orders:
            self.simulation.pushEvent(EventOrder(timestamp + self.getLatency(), order, self.simulation.orderbooks[trade.symbol]))

    
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
    def __init__(self, agent: Agent, price: float, symbol: list, quantity: int, buy: bool):
        super().__init__(agent)
        self.price = price
        self.symbol = symbol
        self.quantity = quantity
        self.buy = buy

    # returns a list of orders to place
    def getOrders(self, symbol: str, timestamp: int):
        order = Order(self, self.buy, symbol, self.quantity, self.price, timestamp)
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
    def __init__(self, agent: Agent, min: int, max: int):
        super().__init__()
        self.minLatency = min
        self.maxLatency = max

    def getLatency(self) -> int:
        return random.randint(self.minLatency, self.maxLatency)

class AgentFixedPrice(Agent):
    def __init__(self, name: str, simulation: 'simulation', price: float, symbol: list, quantity: int, buy: bool):
        super().__init__(name, simulation)
        self.balance = 10000.0
        self.price = price
        self.symbols = symbol
        self.quantity = quantity
        self.buy = buy

    def inputData(self, trade: 'Trade', timestamp: int):
        #print(timestamp)
        super().inputData(trade, timestamp)
        self.trade(trade.symbol, timestamp)

    def getLatency(self) -> int:
        return int(random.random() * 100)
        #return 1

    def trade(self, symbol: str, timestamp: int):
        order = Order(self, self.buy, symbol, self.quantity, self.price, timestamp)
        self.simulation.pushEvent(EventOrder(timestamp + self.getLatency(), order, self.simulation.orderbooks[symbol]))

# todo - add multiple agent types

# one agent will use a simple algorithm
# another could be a market maker w/ historical data