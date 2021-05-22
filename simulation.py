from os import system
from events import *
from agents import *
import numpy as np
import json
class Simulation:
    def __init__(self, file: str = None):
        self.eventQueue = EventQueue(self)
        self.agents = list()
        self.agentGroups = list()
        self.orderbooks = dict()
        self.startingPrices = dict()
        self.maxTime = 0
        self.debugPrint = False

        if file is not None:
            self.loadFile(file)
        # look at algorithms, see what happens in simulation, read more later
        # normal distribution, mean = distance from exchange, variance = quality of network
        # volatility metric?

        self.tradesCount = 0

        for o in self.orderbooks:
            self.broadcastTradeInfo([Trade(None, None, None, None, self.startingPrices[o], o, 0, 0)])
    
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

    def broadcastTradeInfo(self, trades):
        for trade in trades:
            self.tradesCount = self.tradesCount + 1
            for agent in self.agents:
                latency: float = agent.latencyFunction.getLatency()
                if trade.timestamp + latency > agent.orderBlockTime:
                    self.eventQueue.queueEvent(EventMarketData(trade.timestamp + latency, trade, agent))

    def pushEvent(self, event: Event):
        self.eventQueue.queueEvent(event)
    
    def makeCancelOrder(self, agent: 'Agent', cancelID: uuid, timestamp: float) -> Order:
        o = Order(agent, False, "", 0, 0, timestamp)
        o.cancel = True
        o.orderID = cancelID
        return o

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
            #i(event.toString()) 

            timestamp = event.time
            oldTime = time
            time = int(event.time / self.maxTime * 100)

            if time != oldTime and self.debugPrint:
                print(time)

                #print(self.orderbooks["A"].toStringShort())

            if event.time > self.maxTime:
                break

            #print(event.toString())
            event.run()

        #buysell = [0, 0]

        #for agent in self.agents:
        #    buysell[0] += agent.algorithm.buysell[0]
        #    buysell[1] += agent.algorithm.buysell[1]

        #print(buysell)
        #print(self.orderbooks["A"].toString())
    
class FundamentalValue:
    def __init__(self, kappa: float, mean: float, shock: float, shockProb: float):
        self.kappa = kappa
        self.mean = mean
        self.shock = shock
        self.shockProb = shockProb

        self.series = list()
        self.series.append(np.random.normal(self.mean, self.shock))

    def computeTo(self, num: int):
        while len(self.series) < num:
            last: float = self.series[len(self.series) - 1]

            if random.random() < self.shockProb:
                self.series.append(np.random.normal(self.mean * self.kappa + last * (1 - self.kappa), self.shock))
            else:
                self.series.append(last)

    def getValue(self, time: int):
        self.computeTo(time)
        return self.series[int(time)]
