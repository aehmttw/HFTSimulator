from events import *
from agents import *
import numpy as np
import json

# This class represents a financial exchange simulation. A config file path can be passed as an argument.
class Simulation:
    def __init__(self, file: str = None):
        self.eventQueue: EventQueue = EventQueue(self)
        self.agents: list = list() # list of Agent
        self.agentGroups: list = list() # list of str
        self.orderbooks: dict = dict() # symbol (str) -> OrderBook
        self.startingPrices: dict = dict() # symbol (str) -> price (float)
        self.maxTime: float = 0
        self.debugPrint: bool = False

        if file is not None:
            self.loadFile(file)

        self.tradesCount = 0

        for o in self.orderbooks:
            self.broadcastTradeInfo([Trade(None, None, None, None, self.startingPrices[o], o, 0, 0)])
    
    # Loads a JSON file configuration for a simulation's settings
    
    # Arguments:
    # runtime (float) - time the simulation runs for, with 1 unit being the time it takes the matching engine to process an order
    # fundamental (dict) - parameters for the simulation fundamental which some agents use (as defined in https://www.jair.org/index.php/jair/article/download/11075/26257)
        # fundamental sub-values:
        # kappa (float) - mean reversion factor
        # mean (float) - mean price value
        # shock (float) - shock factor
        # prob (float) - probability per time unit for the price to change at all
    # symbols (dict) - dict of symbols, symbol name (str) -> symbol starting price (float)
    # agents (dict) - all the simulation agents. See Agent's fromJson() for more.
    def loadFile(self, file: str):
        with open(file) as f:
            j = json.loads(f.read())
        
        self.maxTime = j["runtime"]

        if j["fundamental"]:
            f = j["fundamental"]
            self.fundamental = FundamentalValue(f["kappa"], f["mean"], f["shock"], f["prob"])


        for s in j["symbols"]:
            self.orderbooks[s] = OrderBook(self, (j["symbols"])[s], s)
            self.startingPrices[s] = (j["symbols"])[s]

        for s in j["agents"]:
            count = 1

            if "count" in s:
                count = s["count"]

            self.agentGroups.append(s["name"])
            
            for i in range(count):
                p: str = ""

                if count > 1:
                    p = str(i)

                self.agents.append(Agent.fromJson(s, self, p))

        for a in self.agents:
            for s in self.startingPrices:
                a.sharePrices[s] = self.startingPrices[s]

    # Information about each trade will be sent to each agent. 
    # One event per agent per trade (as each agent receives information about the trade at a different time).
    def broadcastTradeInfo(self, trades):
        for trade in trades:
            self.tradesCount = self.tradesCount + 1
            for agent in self.agents:
                latency: float = agent.latencyFunction.getLatency()
                if trade.timestamp + latency > agent.orderBlockTime:
                    self.eventQueue.queueEvent(EventMarketData(trade.timestamp + latency, trade, agent))

    # Add an event to the event queue
    def pushEvent(self, event: Event):
        self.eventQueue.queueEvent(event)
    
    # Creates and returns a cancel order with the specified order ID. Cancel orders can be submitted to cancel one specific order.
    def makeCancelOrder(self, agent: 'Agent', cancelID: uuid, timestamp: float) -> Order:
        o = Order(agent, False, "", 0, 0, timestamp)
        o.cancel = True
        o.orderID = cancelID
        return o

    # Runs the simulation
    def run(self):
        events = 0

        time: int = 0
        timestamp: float = 0

        while True:
            if self.eventQueue.isEmpty():
                for o in self.orderbooks:
                    self.broadcastTradeInfo([Trade(None, None, None, None, self.orderbooks[o].price, o, 0, timestamp)])

            if self.eventQueue.isEmpty():
                t: float = float("inf")

                for a in self.agents:
                    t = min(a.orderBlockTime, t)
                
                timestamp = t
                continue

            events += 1
            event = self.eventQueue.nextEvent()

            timestamp = event.time
            oldTime = time
            time = int(event.time / self.maxTime * 100)

            if time != oldTime and self.debugPrint:
                print(time)

            if event.time > self.maxTime:
                break

            event.run()

# Some agents as described in an article use a global simulation fundamental to model the price instead of using market data.    
class FundamentalValue:
    def __init__(self, kappa: float, mean: float, shock: float, shockProb: float):
        self.kappa = kappa
        self.mean = mean
        self.shock = shock
        self.shockProb = shockProb

        self.series = list()
        self.series.append(np.random.normal(self.mean, self.shock))

    # Calculates the fundamental's value up to the given time
    def computeTo(self, num: int):
        while len(self.series) < num:
            last: float = self.series[len(self.series) - 1]

            if random.random() < self.shockProb:
                self.series.append(np.random.normal(self.mean * self.kappa + last * (1 - self.kappa), self.shock))
            else:
                self.series.append(last)

    # Returns the fundamental's price value at the given time
    def getValue(self, time: int):
        self.computeTo(time)
        return self.series[int(time)]
