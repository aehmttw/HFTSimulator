from orderbook import *
from order import *
from events import *
import random
class Agent:
    def __init__(self, name: str, simulation: 'Simulation'):
        self.balance = 10000.0
        self.name = name
        self.simulation = simulation
        
        # Symbol -> amount
        self.shares = dict()
        self.shares["A"] = 100

        self.baseLatency = 0

        self.orderBooks = dict()
        self.sharePrices = dict()
     
    def inputData(self, trade: 'Trade', timestamp: int):
        self.sharePrices[trade.symbol] = trade.price
        # How to handle un-matched trades?
        

    # Returns an Order telling what to do, or noOrder if nothing should be done
    # Make sure to set the order timestamp based on the latency
    def trade(self): # Limit order book as input or trades (market data)
        raise NotImplementedError #instead of return add to queue
    
    # Returns a latency for an action
    # If latency varies for each action by a bit, that variation can be added here to a base latency
    # Maybe add other latencies to separate places too, depending on how this will be implemented
    def getLatency(self) -> int:
        raise NotImplementedError

# market maker - could schedule events at for self
# maybe plot event queue size over time to see how long to simulate for, to see practicality

class AgentFixedPrice(Agent):
    def __init__(self, name: str, simulation: 'simulation', price: float, symbol: list, quantity: int, buy: bool):
        super().__init__(name, simulation)
        self.balance = 10000.0
        self.price = price
        self.symbols = symbol
        self.quantity = quantity
        self.buy = buy

    def inputData(self, trade: 'Trade', timestamp: int):
        super().inputData(trade, timestamp)
        self.trade(trade.symbol, timestamp)

    def getLatency(self) -> int:
        return int(random.random() * 100)

    def trade(self, symbol: str, timestamp: int):
        order = Order(self, self.buy, symbol, self.quantity, self.price, timestamp)
        self.simulation.pushEvent(EventOrder(timestamp + self.getLatency(), order, self.simulation.orderbooks[symbol]))






# todo - add multiple agent types

# one agent will use a simple algorithm
# another could be a market maker w/ historical data