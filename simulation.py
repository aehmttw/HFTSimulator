from typing_extensions import runtime
from events import *
from agents import *
import json
class Simulation:
    def __init__(self, file: str = None):
        self.eventQueue = EventQueue(self)
        self.agents = list()
        self.orderbooks = dict()
        self.startingPrices = dict()
        self.maxTime = 0

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

        for s in j["symbols"]:
            self.orderbooks[s] = OrderBook(self, (j["symbols"])[s])
            self.startingPrices[s] = (j["symbols"])[s]

        for s in j["agents"]:
            self.agents.append(Agent.fromJson(s, self))

    def broadcastTradeInfo(self, trades):
        for trade in trades:
            self.tradesCount = self.tradesCount + 1
            for agent in self.agents:
                self.eventQueue.queueEvent(EventMarketData(trade.timestamp + agent.latencyFunction.getLatency(), trade, agent))

    def pushEvent(self, event: Event):
        self.eventQueue.queueEvent(event)
    
    def makeCancelOrder(self, agent: 'Agent', cancelID: uuid, timestamp: float) -> Order:
        o = Order(agent, False, "", 0, 0, timestamp)
        o.cancel = True
        o.orderID = cancelID
        return o

    def run(self):
        events = 0
        while not self.eventQueue.isEmpty():
            events += 1
            event = self.eventQueue.nextEvent()

            if event.time > self.maxTime:
                break

            print(event.toString())
            event.run()

        #print(self.orderbooks["A"].toString())

            # test to make sure this is working correctly
            # algorithms and graphing, plots at end of simulation (what are we interested in?) - things like price, volatility and relation to hypothesis
            # first blog post - talk about design, simulator



# add push event method to internally push an event (can post-process here)
# design diagram of how these classes interact with each other


# call next event, process event, which can push back