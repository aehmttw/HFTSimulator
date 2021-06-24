from orderbook import *
from order import *
from events import *
import random

# This class defines a trader on a stock exchange. 
class Agent:

    # Each agent has a name, a simulation upon which it operates, and an initial cash balance and share quantities.
    # "shares" should be passed as a dictionary, with keys being the stock symbols and values indicating the number of that share owned.
    def __init__(self, name: str, simulation: 'Simulation', balance: float, shares: dict):
        self.balance: float = balance
        self.name: str = name
        self.simulation: 'Simulation' = simulation

        # When set, market data will be ignored until the simulation time equals this variable's time
        self.orderBlockTime: float = -1

        # Statistics for number of orders sent, matched, and canceled
        self.sentOrders: int = 0
        self.canceledOrders: int = 0
        self.matchedOrders: int = 0
     
        # Prices at which this agent matched
        # List of floats
        self.pricesMatched: list = list()
        self.pricesMatchedBuy: list = list()
        self.pricesMatchedSell: list = list()

        # How many times this agent matched with other agents
        # Key: agent group name, Value: number of times matched
        self.agentsMatched: dict = dict()
        self.agentsMatchedBuy: dict = dict()
        self.agentsMatchedSell: dict = dict()
        
        # Prices at which this agent matched, per agent
        # Key: agent group name, Value: a list, storing the prices at which it matched
        self.agentPricesMatchedBuy: dict = dict()
        self.agentPricesMatchedSell: dict = dict()

        # How much of each share this agent owns
        # Key: symbol (str), Value: amount (int)
        self.shares = shares

        # A storage of at what prices different stocks last transacted at
        # Key: symbol (str), Value: price (float)
        self.sharePrices = dict()

        self.algorithm = None
        self.latencyFunction = None

    # Parses an agent from a json dictionary
    # Takes: a json dictionary, a simulation, and an index integer
    # The same json dictionary can define multiple identical agents - the index integer is used to differentiate them

    # Json properties for each agent: 
    # count (int) - set to more than 1 to have multiple identical copies of the agent in the simulation (all copies will be grouped)
    # name (str) - the agent's name
    # balance (float) - how much cash this agent starts with
    # type (str) - the agent's type
    # typeargs (dict) - additional arguments specific to the agent type - see each agent's class to see its type args
    # shares (dict: str -> int) - how many of each share this agent starts with, Key: symbol (str), Value: amount (int)
    # algtype (str) - the agent's algorithm type
    # algargs (str) - additional arguments specific to the algorithm type - see each algorithm's class to see its type args
    # latency (str) - a latency function, like "linear" or "normal"
    # latencyargs (dict) - additional arguments specific to the latency function - see each latency function's class to see its args
    def fromJson(j: dict, simulation: 'Simulation', index: int) -> 'Agent':
        # Multiple agents created from 1 json dictionary will be named like "agent0", "agent1", "agent2", etc.
        name: str = j["name"] + index
        balance: float = j["balance"]
        
        type: str = j["type"]
        args: dict = j["typeargs"]

        shares: dict = j["shares"].copy()

        agent: Agent = None
        if type == "basic":
            agent = BasicAgent(name, simulation, balance, shares, args)
        elif type == "canceling":
            agent = CancelingAgent(name, simulation, balance, shares, args)
        elif type == "recording":
            agent = RecordingAgent(name, simulation, balance, shares, args)
        elif type == "basicmarketmaker":
            agent = BasicMarketMakerAgent(name, simulation, balance, shares, args)
        elif type == "regulartrading":
            agent = RegularTradingAgent(name, simulation, balance, shares, args)
        elif type == "poisson":
            agent = PoissonAgent(name, simulation, balance, shares, args)
        elif type == "stalequotearbitrage":
            agent = StaleQuoteArbitrageAgent(name, simulation, balance, shares, args)

        # Agents created from the same json dictionary will be grouped together
        agent.groupName = j["name"]

        algtype: str = j["algorithm"]
        algargs: dict = j["algorithmargs"]

        algorithm: Algorithm = None

        if algtype == "fixedprice":
            algorithm = AlgorithmFixedPrice(agent, algargs)
        elif algtype == "randomnormal":
            algorithm = AlgorithmRandomNormal(agent, algargs)
        elif algtype == "randomlognormal":
            algorithm = AlgorithmRandomLogNormal(agent, algargs)
        elif algtype == "randomlinear":
            algorithm = AlgorithmRandomLinear(agent, algargs)
        elif algtype == "buylowsellhigh":
            algorithm = AlgorithmBuyLowSellHigh(agent, algargs)
        elif algtype == "meanreversion":
            algorithm = AlgorithmMeanReversion(agent, algargs)
        elif algtype == "simplemarketmaker":
            algorithm = AlgorithmSimpleMarketMaker(agent, algargs)
        elif algtype == "fixedmarketmaker":
            algorithm = AlgorithmMarketMakerFixed(agent, algargs)
        elif algtype == "fundamentalmarketmaker":
            algorithm = AlgorithmFundamentalMM(agent, algargs)
        elif algtype == "zi":
            algorithm = AlgorithmZI(agent, algargs)
        elif algtype == "stalequotearbitrage":
            algorithm = AlgorithmStaleQuoteArbitrage(agent, algargs)
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

    # Called whenever data of a newly matched trade is received.
    def inputData(self, trade: Trade, timestamp: float):
        raise NotImplementedError

    # Attempts to create and submit an order. Fails if insufficient cash or shares.
    # Used by some agents which do not want to go in the negatives. Others submit directly.
    def attemptCreateOrder(self, timestamp: float, order: Order, symbol: str) -> bool:
        if order.buy and self.balance < order.amount * self.sharePrices[symbol]:
            return False
        
        if not order.buy and self.shares[symbol] < order.amount:
            return False

        self.simulation.pushEvent(EventOrder(timestamp + self.latencyFunction.getLatency(), order, self.simulation.orderbooks[symbol]))
        return True

# A very simple agent which simply sends in a new order when it receives market data.
# Does not take any further args

# Generally having a lot of these agents in a simulation results in orders being sent with exponentially increasing frequency,
# if there are more than 2 of them.
class BasicAgent(Agent):
    def __init__(self, name: str, simulation: 'Simulation', balance: float, shares: dict, args: dict):
        super().__init__(name, simulation, balance, shares)

    def inputData(self, trade: 'Trade', timestamp: float):
        self.sharePrices[trade.symbol] = trade.price
        orders: list = self.algorithm.getOrders(trade.symbol, timestamp)

        for order in orders:
            self.attemptCreateOrder(timestamp, order, trade.symbol)

# A slightly more complex version of the Basic Agent
# This agent will cancel its orders a certain amount of time after thay're sent, if they haven't matched
# It will also refuse new market data a certain amount of time after sending an order

# Arguments:
# orderlifespan: float - how long each order can stay in the order book before being canceled
# orderchance: float - value from 0-1 indicating probability of submitting a new order upon receiving new market data
# ordercooldown: float - time waited after sending an order before again accepting more market data
class CancelingAgent(Agent):
    def __init__(self, name: str, simulation: 'Simulation', balance: float, shares: dict, args: dict):
        super().__init__(name, simulation, balance, shares)

        # Orders sent which haven't been canceled yet
        self.activeOrders: list = list()
        self.orderLifespan: float = args["orderlifespan"]
        self.orderChance: float = args["orderchance"]
        self.orderCooldown: float = args["ordercooldown"]
        self.orderBlockTime = random.random() * self.orderCooldown
        #todo - make this block for multiple books

    def inputData(self, trade: 'Trade', timestamp: float):
        self.sharePrices[trade.symbol] = trade.price

        # Cancel old orders
        for order in self.activeOrders:
            if timestamp - order.timestamp >= self.orderLifespan:
                self.simulation.pushEvent(EventOrder(timestamp + self.latencyFunction.getLatency(), self.simulation.makeCancelOrder(self, order.orderID, timestamp), self.simulation.orderbooks[trade.symbol]))
        
        if random.random() >= self.orderChance:
            return

        orders = self.algorithm.getOrders(trade.symbol, timestamp)
        
        for order in orders:
            if self.attemptCreateOrder(timestamp, order, trade.symbol):
                self.activeOrders.append(order)
        
        self.orderBlockTime = timestamp + self.orderCooldown

# An agent which sends orders on its own on times based on a poisson distribution
# Arguments: reentryrate (float) - rate at which the agent sends orders
class PoissonAgent(Agent):
    def __init__(self, name: str, simulation: 'Simulation', balance: float, shares: dict, args: dict):
        super().__init__(name, simulation, balance, shares)
        self.rate: float = args["reentryrate"]
        self.simulation.pushEvent(EventScheduleAgent(-numpy.log(random.random()) / self.rate, self))

    def inputData(self, trade: 'Trade', timestamp: float):
        self.sharePrices[trade.symbol] = trade.price

    def inputOrders(self, timestamp: float):
        self.simulation.pushEvent(EventScheduleAgent(-numpy.log(random.random()) / self.rate + timestamp, self))
        
        for s in self.simulation.orderbooks:
            orders = self.algorithm.getOrders(s, timestamp)

            for order in orders:
                self.simulation.pushEvent(EventOrder(timestamp + self.latencyFunction.getLatency(), order, self.simulation.orderbooks[s]))

# Agent which saves past prices of transactions, for a certain time interval; useful for mean reversion traders

# Arguments:
# orderlifespan: float - how long each order can stay in the order book before being canceled
# orderchance: float - value from 0-1 indicating probability of submitting a new order upon receiving new market data
# timeinterval: float - prices of transactions older than this value are discarded
class RecordingAgent(Agent):
    def __init__(self, name: str, simulation: 'Simulation', balance: float, shares: dict, args: dict):
        super().__init__(name, simulation, balance, shares)
       
        # Orders sent which haven't been canceled yet
        self.activeOrders: list = list()
        self.orderLifespan: float = args["orderlifespan"]
        self.orderChance: float = args["orderchance"]
        self.timeInterval: float = args["timeinterval"]

        self.pastPrices: list = list()
        self.pastPriceTimes: list = list()

    def inputData(self, trade: 'Trade', timestamp: float):
        # Save transaction price
        self.sharePrices[trade.symbol] = trade.price
        self.pastPrices.append(trade.price)
        self.pastPriceTimes.append(timestamp)

        # Purge old transaction prices
        while len(self.pastPriceTimes) > 0 and timestamp - self.pastPriceTimes[0] > self.timeInterval:
            self.pastPriceTimes.remove(self.pastPriceTimes[0])
            self.pastPrices.remove(self.pastPrices[0])

        # Cancel old orders
        for order in self.activeOrders:
            if timestamp - order.timestamp >= self.orderLifespan:
                self.simulation.pushEvent(EventOrder(timestamp + self.latencyFunction.getLatency(), self.simulation.makeCancelOrder(self, order.orderID, timestamp), self.simulation.orderbooks[trade.symbol]))
        
        if random.random() >= self.orderChance:
            return

        # Send orders
        orders = self.algorithm.getOrders(trade.symbol, timestamp)
        
        for order in orders:
            if self.attemptCreateOrder(timestamp, order, trade.symbol):
                self.activeOrders.append(order)

# Simple market maker agent which saves the last buy and sell prices and reacts to new market data
# No arguments  
class BasicMarketMakerAgent(Agent):
    def __init__(self, name: str, simulation: 'Simulation', balance: float, shares: dict, args: dict):
        super().__init__(name, simulation, balance, shares)
        self.lastBuy: dict = dict()
        self.lastSell: dict = dict()

    def inputData(self, trade: 'Trade', timestamp: float):
        if trade.buyOrder is not None and trade.sellOrder is not None:
            if trade.buyOrder.timestamp < trade.sellOrder.timestamp:
                self.lastBuy[trade.symbol] = trade.buyOrder.price
            else:
                self.lastSell[trade.symbol] = trade.sellOrder.price
        
        self.sharePrices[trade.symbol] = trade.price
        orders = self.algorithm.getOrders(trade.symbol, timestamp)

        for order in orders:
            self.attemptCreateOrder(timestamp, order, trade.symbol)

# Agent which trades every certain time interval
# Arguments: interval (float)
class RegularTradingAgent(Agent):
    def __init__(self, name: str, simulation: 'Simulation', balance: float, shares: dict, args: dict):
        super().__init__(name, simulation, balance, shares)
        self.interval: float = args["interval"]
        self.simulation.pushEvent(EventScheduleAgent(self.interval, self))

    def inputData(self, trade: 'Trade', timestamp: float):
        self.sharePrices[trade.symbol] = trade.price

    def inputOrders(self, timestamp: float):
        self.simulation.pushEvent(EventScheduleAgent(self.interval + timestamp, self))

        for s in self.simulation.orderbooks:
            orders = self.algorithm.getOrders(s, timestamp)

            for order in orders:
                self.attemptCreateOrder(timestamp, order, s)

# An agent which requests the order book regularly and saves the 10 best deals on both sides
# Agent which trades every certain time interval
# Arguments: interval (float), symbol (str) - the symbol to trade on
class StaleQuoteArbitrageAgent(Agent):
    def __init__(self, name: str, simulation: 'Simulation', balance: float, shares: dict, args: dict):
        super().__init__(name, simulation, balance, shares)
        self.activeOrders: list = list()
        self.interval: float = args["interval"]
        self.symbol: str = args["symbol"]
        self.simulation.pushEvent(EventScheduleAgent(self.interval, self))

    def inputData(self, trade: 'Trade', timestamp: float):
        pass

    def inputOrders(self, timestamp: float):
        self.simulation.pushEvent(EventScheduleAgent(self.interval + timestamp, self))
        self.simulation.pushEvent(EventRequestOrderbook(self.latencyFunction.getLatency() + timestamp, self, self.symbol, 10))

    def inputOrderBooks(self, timestamp: float, buybook: list, sellbook: list):
        self.lastBuyBook: list = buybook
        self.lastSellBook: list = sellbook

        for o in self.activeOrders:
            self.simulation.pushEvent(EventOrder(timestamp + self.latencyFunction.getLatency(), self.simulation.makeCancelOrder(self, o.orderID, timestamp), self.simulation.orderbooks[o.symbol]))

        self.activeOrders.clear()

        for s in self.simulation.orderbooks:
            orders = self.algorithm.getOrders(s, timestamp)

            for o in orders:
                self.activeOrders.append(o)

            for order in orders:
                self.simulation.pushEvent(EventOrder(timestamp + self.latencyFunction.getLatency(), order, self.simulation.orderbooks[s]))

# A factor used by the Zero Intelligence algorithm
# Args: max position, variation
class PrivateValue:
    def __init__(self, m: int, var: float):

        # Maximum number of shares that can be owned (positive and negative)
        self.maxPos: int = m

        # Descending sorted list of values pulled from a normal distribution
        self.values: list = list()

        for i in range(m * 2):
            self.values.append(numpy.random.normal(0, var))

        numpy.sort(self.values)
        self.values.reverse()
    
    def getValue(self, pos: int, buy: bool):
        if buy:
            return self.values[max(pos + self.maxPos, 0)]
        else:
            return self.values[min(pos + self.maxPos - 1, len(self.values) - 1)]

# This class defines an algorithm that can be used by an agent 
class Algorithm:
    def __init__(self, agent: Agent):
        self.agent = agent

    # returns a list of orders to place
    def getOrders(self, symbol: str, timestamp: float):
        raise NotImplementedError

# Algorithm which always sends out the same order
# args = price: float, quantity: int, buy: bool
class AlgorithmFixedPrice(Algorithm):
    # This class defines an algorithm that can be used by an agent 
    def __init__(self, agent: Agent, args: dict):
        super().__init__(agent)
        self.price: float = args["price"]
        self.quantity: int = args["quantity"]
        self.buy: bool = args["buy"]

    # returns a list of orders to place
    def getOrders(self, symbol: str, timestamp: float):
        order = Order(self.agent, self.buy, symbol, self.quantity, self.price, timestamp)
        return [order]

# Algorithm which sends an order with price picked from normal distribution around the last transaction price
# Number of orders to send is picked uniformly between a minimum and maximum number given

# Arguments:
# spread: float - standard deviation of the normal distribution
# quantitymin: int - minimum number of orders sent
# quantitymax: int - maximum number of orders sent
class AlgorithmRandomNormal(Algorithm):
    def __init__(self, agent: Agent, args: dict):
        super().__init__(agent)
        self.spread: float = args["spread"]
        self.quantityMin: int = args["quantitymin"]
        self.quantityMax: int = args["quantitymax"]

    # returns a list of orders to place
    def getOrders(self, symbol: str, timestamp: float):
        price: float = self.agent.sharePrices[symbol]
        buy: bool = random.randint(1, 2) == 1
        quantity: int = random.randint(self.quantityMin, self.quantityMax)
        order = Order(self.agent, buy, symbol, quantity, round(numpy.random.normal(price, self.spread * price), 2), timestamp)
        return [order]

# Algorithm which sends an order with price picked from log normal distribution around the last transaction price
# Number of orders to send is picked uniformly between a minimum and maximum number given

# Arguments:
# spread: float - spread of the distribution
# quantitymin: int - minimum number of orders sent
# quantitymax: int - maximum number of orders sent
# buychance: float - from 0 to 1, chance to buy ([1 - this value] is the chance to sell)
class AlgorithmRandomLogNormal(Algorithm):
    def __init__(self, agent: Agent, args: dict):
        super().__init__(agent)
        self.spread: float = args["spread"]
        self.quantityMin: int = args["quantitymin"]
        self.quantityMax: int = args["quantitymax"]
        self.buyChance: float = args["buychance"]

    # returns a list of orders to place
    def getOrders(self, symbol: str, timestamp: float):
        price: float = self.agent.sharePrices[symbol]
        buy: bool = random.random() < self.buyChance
        quantity: int = random.randint(self.quantityMin, self.quantityMax)
        order = Order(self.agent, buy, symbol, quantity, round(price * numpy.random.lognormal(0, self.spread), 2), timestamp)
        return [order]

# Algorithm which sends an order with price picked from uniformly around the last transaction price
# Number of orders to send is picked uniformly between a minimum and maximum number given

# Arguments:
# spread: float - spread of the linear distribution
# quantitymin: int - minimum number of orders sent
# quantitymax: int - maximum number of orders sent
class AlgorithmRandomLinear(Algorithm):
    def __init__(self, agent: Agent, args: dict):
        super().__init__(agent)
        self.spread: float = args["spread"]
        self.quantityMin: int = args["quantitymin"]
        self.quantityMax: int = args["quantitymax"]

    # returns a list of orders to place
    def getOrders(self, symbol: str, timestamp: float):
        price: float = self.agent.sharePrices[symbol]
        buy: bool = random.randint(1, 2) == 1
        quantity: int = random.randint(self.quantityMin, self.quantityMax)
        order = Order(self.agent, buy, symbol, quantity, round(((random.random() * 2 - 1) * self.spread + 1) * price, 2), timestamp)
        return [order]

# Algorithm which buys or sells when prices pass a certain threshold
# Number of orders to send is picked uniformly between a minimum and maximum number given

# Arguments:
# buythreshold: float - maximum price to buy
# sellthreshold: float - minimum price to sell
# quantitymin: int - minimum number of orders sent
# quantitymax: int - maximum number of orders sent
class AlgorithmBuyLowSellHigh(Algorithm):
    def __init__(self, agent: Agent, args: dict):
        super().__init__(agent)
        self.buyThreshold: float = args["buythreshold"]
        self.sellThreshold: float = args["sellthreshold"]
        self.quantityMin: float = args["quantitymin"]
        self.quantityMax: float = args["quantitymax"]

    # returns a list of orders to place
    def getOrders(self, symbol: str, timestamp: float):
        price: float = self.agent.sharePrices[symbol]
        
        buy = False
        if price <= self.buyThreshold:
            buy = True
        elif price >= self.sellThreshold:
            buy = False
        else:
            return []

        quantity: int = random.randint(self.quantityMin, self.quantityMax)
        order = Order(self.agent, buy, symbol, quantity, round(price, 2), timestamp)
        return [order]

# Algorithm which uses mean reversion - averages prices from the last time interval; if current price is far off from those, it sends an order
# Number of orders to send is picked uniformly between a minimum and maximum number given
# REQUIRES AGENT TO BE A RecordingAgent

# Arguments:
# quantitymin: int - minimum number of orders sent
# quantitymax: int - maximum number of orders sent
# threshold: float - if current price is farther than this value times the average over the time interval, an order is sent

class AlgorithmMeanReversion(Algorithm):
    def __init__(self, agent: RecordingAgent, args: dict):
        super().__init__(agent)
        self.quantityMin: float = args["quantitymin"]
        self.quantityMax: float = args["quantitymax"]
        self.threshold: float = args["threshold"]

    # returns a list of orders to place
    def getOrders(self, symbol: str, timestamp: float):
        price: float = self.agent.sharePrices[symbol]
        
        sum = 0
        for price in self.agent.pastPrices:
            sum += price

        avg = sum / len(self.agent.pastPrices);
        if price <= avg + avg * self.threshold and price >= avg - avg * self.threshold:
            return []
        else:    
            buy = price < avg 
        
        quantity: int = random.randint(self.quantityMin, self.quantityMax)
        order = Order(self.agent, buy, symbol, quantity, round(price, 2), timestamp)
        return [order]

# Zero Intelligence Agent based on as defined here: https://www.jair.org/index.php/jair/article/download/11075/26257
# offsetmin: float - minimum price offset from price valuation to try to guarantee profit when sending order
# offsetmax: float - maximum price offset from price valuation to try to guarantee profit when sending order
# positionmax: int - absolute value of max number of shares (for example, value of 5 means we can have -5 to 5 shares)
# variation: float - variation in private value list
class AlgorithmZI(Algorithm):
    def __init__(self, agent: Agent, args: dict):
        super().__init__(agent)
        self.offsetMin: float = args["offsetmin"]
        self.offsetMax: float = args["offsetmax"]
        self.privateValue: PrivateValue = PrivateValue(args["positionmax"], args["variation"])
        self.orders = list()

    def getOrders(self, symbol: str, timestamp: float):
        price: float = self.agent.simulation.fundamental.getValue(timestamp)
        position: int = self.agent.shares[symbol]

        buy: bool = random.random() < 0.5

        if position >= self.privateValue.maxPos - 1:
            buy = False
        elif position <= -self.privateValue.maxPos + 1:
            buy = True
        
        price += self.privateValue.getValue(position, buy)

        mul: int = 1

        if buy:
            mul = -1

        cancelOrders = list()
        for order in self.orders:
            cancelOrders.append(self.agent.simulation.makeCancelOrder(self.agent, order.orderID, timestamp))

        price += mul * random.random() * (self.offsetMax - self.offsetMin) + self.offsetMin
        order: Order = Order(self.agent, buy, symbol, 1, round(price, 2), timestamp)
        self.orders = [order]
        return self.orders + cancelOrders

# Market Maker based on as defined here: https://www.jair.org/index.php/jair/article/download/11075/26257
# spread: float - minimum gap between simulation fundamental and order price sent
# tickspread: float - gap between further sent orders
# tickcount: int - max amount of sent orders on each side
class AlgorithmFundamentalMM(Algorithm):
    def __init__(self, agent: Agent, args: dict):
        super().__init__(agent)
        self.orders: list = list()
        self.spread: float = args["spread"]
        self.tickSpread: float = args["tickspread"]
        self.tickCount: int = args["tickcount"]

    def getOrders(self, symbol: str, timestamp: float):
        price: float = self.agent.simulation.fundamental.getValue(timestamp)
        #for now, assumes 0 latency
        book: OrderBook = self.agent.simulation.orderbooks[symbol]

        hasBuy: bool = False
        hasSell: bool = False

        if len(book.buybook) > 0:
            hasBuy = True
            bestbuy = heapq.heappop(book.buybook)
            heapq.heappush(book.buybook, bestbuy)

        if len(book.sellbook) > 0:
            hasSell = True
            bestsell = heapq.heappop(book.sellbook)
            heapq.heappush(book.sellbook, bestsell)

        cancelOrders = list()
        for order in self.orders:
            cancelOrders.append(self.agent.simulation.makeCancelOrder(self.agent, order.orderID, timestamp))

        self.orders = list()
        for i in range(self.tickCount):
            p: float = price + self.tickSpread * i + self.spread
            p2: float = price - self.tickSpread * i - self.spread
            #print(str(p) + " " + str(p2))

            if not hasBuy or p < bestbuy[2].price:
                #bprices.append(round(p, 2))
                self.orders.append(Order(self.agent, True, symbol, 1, round(p, 2), timestamp))

            if not hasSell or p2 > bestsell[2].price:
                #sprices.append(round(p2, 2))
                self.orders.append(Order(self.agent, False, symbol, 1, round(p2, 2), timestamp))

        #print(str(bprices) + " " + str(sprices))
        return self.orders + cancelOrders

# Stale Quote Arbitrage agent - attempts to match with "good deal" (stale) orders which no longer reflect the current price
# Arguments: threshold (float) - threshold difference between simulation fundamental and price to trigger an attempted match
class AlgorithmStaleQuoteArbitrage(Algorithm):
    def __init__(self, agent: Agent, args: dict):
        super().__init__(agent)
        self.threshold: float = args["threshold"]
        
    def getOrders(self, symbol: str, timestamp: float):
        orders = list()

        price = self.agent.simulation.fundamental.getValue(timestamp)
        
        for order in self.agent.lastBuyBook:
            if price - order[2].price < self.threshold:
                orders.append(order[2])

        for order in self.agent.lastSellBook:
            if order[2].price - price < self.threshold:
                orders.append(order[2])
        
        #print(str(len(self.agent.lastBuyBook) + len(self.agent.lastSellBook)) + " " + str(len(orders)))

        submitOrders = list()
        for order in orders:
            submitOrders.append(Order(self.agent, not order.buy, order.symbol, order.amount, order.price, timestamp))

        return submitOrders

# Simple market maker - looks at the last sell and buy prices transacted and tries to offer a better deal
# AGENT MUST BE A BasicMarketMakerAgent

# Arguments:
# distance: float - how much better the deal offered is
# quantity: int - number of orders to send
class AlgorithmSimpleMarketMaker(Algorithm):
    def __init__(self, agent: BasicMarketMakerAgent, args: dict):
        super().__init__(agent)
        self.distance: float = args["distance"]
        self.quantity: int = args["quantity"]
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

# Market maker which shapes the price of the stock by sending many buy and sell orders around the desired price curve
# Key frames are given and interpolated to produce the desired price curve

# Arguments:
# quantity: int - number of orders to send each tick
# spread: float - distance from price curve at which order prices are
# prices: list of float - key frames for prices
# interval: distance in time between key frames
class AlgorithmMarketMakerFixed(Algorithm):
    def __init__(self, agent: BasicMarketMakerAgent, args: dict):
        super().__init__(agent)
        self.quantity = args["quantity"]
        self.lastBuy: Order = None
        self.lastSell: Order = None
        self.spread: float = args["spread"]
        self.prices: list = args["prices"]
        self.priceInterval: float = args["interval"]

    # returns a list of orders to place
    def getOrders(self, symbol: str, timestamp: float):
        orders = list()

        price = 0
        if timestamp >= (len(self.prices) - 1) * self.priceInterval:
            price = self.prices[len(self.prices) - 1]
        else:
            index = timestamp / self.priceInterval
            price = self.prices[int(index)] * (1 - (index % 1)) + self.prices[int(index + 1)] * (index % 1)

        if self.lastBuy is not None and self.lastSell is not None:
            orders.append(self.agent.simulation.makeCancelOrder(self.agent, self.lastBuy.orderID, timestamp))
            orders.append(self.agent.simulation.makeCancelOrder(self.agent, self.lastSell.orderID, timestamp))
     
        self.lastBuy = Order(self.agent, True, symbol, self.quantity, price - self.spread / 2, timestamp)
        orders.append(self.lastBuy)

        self.lastSell = Order(self.agent, False, symbol, self.quantity, price + self.spread / 2, timestamp)
        orders.append(self.lastSell)

        orders.append(Order(self.agent, True, symbol, 1, price, timestamp))
        orders.append(Order(self.agent, False, symbol, 1, price, timestamp))

        return orders

# This class defines a latency distribution function that can be used by an agent
class LatencyFunction:
    def __init__(self, agent: Agent):
        self.agent = agent

    # returns a latency value
    def getLatency(self) -> float:
        raise NotImplementedError

# Linear latency function: latency is linearly between min and max parameters
# args = min: float, max: float
class LatencyFunctionLinear(LatencyFunction):
    def __init__(self, agent: Agent, args: dict):
        super().__init__(agent)
        self.minLatency = args["min"]
        self.maxLatency = args["max"]

    def getLatency(self) -> float:
        return random.random() * (self.maxLatency - self.minLatency) + self.minLatency

# Normal distribution latency function: latency follows a normal distribution with given mean and deviation
# args = mean: float, deviation: float
class LatencyFunctionNormal(LatencyFunction):
    def __init__(self, agent: Agent, args: dict):
        super().__init__(agent)
        self.meanLatency = args["mean"]
        self.latencyDeviation = args["deviation"]

    def getLatency(self) -> float:
        return max(0, numpy.random.normal(self.meanLatency, self.latencyDeviation))
