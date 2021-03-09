from orderbook import *
from order import *
from events import *
import random
class Agent:
    def __init__(self, name: str, simulation: 'Simulation', balance: float, shares: dict):
        self.balance = balance
        self.name = name
        self.simulation = simulation
        self.orderBlockTime = -1
        
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
        elif type == "canceling":
            agent = CancelingAgent(name, simulation, balance, shares, args)
        elif type == "basicmarketmaker":
            agent = BasicMarketMakerAgent(name, simulation, balance, shares, args)

        algtype: str = j["algorithm"]
        algargs: dict = j["algorithmargs"]

        algorithm: Algorithm = None

        if algtype == "fixedprice":
            algorithm = AlgorithmFixedPrice(agent, algargs)
        elif algtype == "randomnormal":
            algorithm = AlgorithmRandomNormal(agent, algargs)
        elif algtype == "randomlinear":
            algorithm = AlgorithmRandomLinear(agent, algargs)
        elif algtype == "simplemarketmaker":
            algorithm = AlgorithmSimpleMarketMaker(agent, algargs)

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

class CancelingAgent(Agent):
    def __init__(self, name: str, simulation: 'Simulation', balance: float, shares: dict, args: dict):
        super().__init__(name, simulation, balance, shares)
        self.activeOrders = list()
        self.orderLifespan = args["orderlifespan"]
        self.orderChance = args["orderchance"]
        self.orderCooldown = args["ordercooldown"]
        self.orderBlockTime = random.random() * self.orderCooldown
        #todo - make this block for multiple books

    def inputData(self, trade: 'Trade', timestamp: float):
        self.sharePrices[trade.symbol] = trade.price

        for order in self.activeOrders:
            if timestamp - order.timestamp >= self.orderLifespan:
                 self.simulation.pushEvent(EventOrder(timestamp + self.latencyFunction.getLatency(), self.simulation.makeCancelOrder(self, order.orderID, timestamp), self.simulation.orderbooks[trade.symbol]))
        
        if random.random() >= self.orderChance:
            return

        orders = self.algorithm.getOrders(trade.symbol, timestamp)
        
        for order in orders:
            self.activeOrders.append(order)
            self.simulation.pushEvent(EventOrder(timestamp + self.latencyFunction.getLatency(), order, self.simulation.orderbooks[trade.symbol]))
        
        self.orderBlockTime = timestamp + self.orderCooldown

class BasicMarketMakerAgent(Agent):
    def __init__(self, name: str, simulation: 'Simulation', balance: float, shares: dict, args: dict):
        super().__init__(name, simulation, balance, shares)
        self.lastBuy = dict()
        self.lastSell = dict()

    def inputData(self, trade: 'Trade', timestamp: float):
        if trade.buyOrder is not None and trade.sellOrder is not None:
            if trade.buyOrder.timestamp < trade.sellOrder.timestamp:
                self.lastBuy[trade.symbol] = trade.buyOrder.price
            else:
                self.lastSell[trade.symbol] = trade.sellOrder.price
        
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
    def __init__(self, agent: Agent, args: dict):
        super().__init__(agent)
        self.spread = args["spread"]
        self.quantityMin = args["quantitymin"]
        self.quantityMax = args["quantitymax"]

    # returns a list of orders to place
    def getOrders(self, symbol: str, timestamp: float):
        price: float = self.agent.sharePrices[symbol]
        buy: bool = random.randint(1, 2) == 1
        order = Order(self.agent, buy, symbol, random.randint(self.quantityMin, self.quantityMax), numpy.random.normal(price, self.spread * price), timestamp)
        return [order]

class AlgorithmRandomLinear(Algorithm):
    def __init__(self, agent: Agent, args: dict):
        super().__init__(agent)
        self.spread = args["spread"]
        self.quantityMin = args["quantitymin"]
        self.quantityMax = args["quantitymax"]

    # returns a list of orders to place
    def getOrders(self, symbol: str, timestamp: float):
        price: float = self.agent.sharePrices[symbol]
        buy: bool = random.randint(1, 2) == 1
        order = Order(self.agent, buy, symbol, random.randint(self.quantityMin, self.quantityMax), ((random.random() * 2 - 1) * self.spread + 1) * price, timestamp)
        return [order]

# Add another market maker with predefined prices
# Going negative issue - prevent trading what one does not have
class AlgorithmSimpleMarketMaker(Algorithm):
    def __init__(self, agent: BasicMarketMakerAgent, args: dict):
        super().__init__(agent)
        self.distance = args["distance"]
        self.quantity = args["quantity"]
        self.lastBuy: Order = None
        self.lastSell: Order = None

    # returns a list of orders to place
    def getOrders(self, symbol: str, timestamp: float):
        orders = list()

        if self.lastBuy is not None and self.lastSell is not None:
            orders.append(self.agent.simulation.makeCancelOrder(self.agent, self.lastBuy.orderID, timestamp))
            orders.append(self.agent.simulation.makeCancelOrder(self.agent, self.lastSell.orderID, timestamp))
        
        if symbol in self.agent.lastBuy and symbol in self.agent.lastSell:
            self.lastBuy = Order(self.agent, True, symbol, self.quantity, self.agent.lastBuy[symbol] + self.distance, timestamp)
            orders.append(self.lastBuy)

            if self.agent.lastBuy[symbol] + self.distance < self.agent.lastSell[symbol] - self.distance:
                self.lastSell = Order(self.agent, False, symbol, self.quantity, self.agent.lastSell[symbol] - self.distance, timestamp)
                orders.append(self.lastSell)

        return orders

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