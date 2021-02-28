from events import *
from agents import *
import time

class Simulation:
    def __init__(self):
        self.eventQueue = EventQueue(self)
        self.agents = list()
        self.orderbooks = dict()
        self.orderbooks["A"] = OrderBook(self)

        self.agents.append(Agent.fromFile("agents/agent1.txt", self))
        self.agents.append(Agent.fromFile("agents/agent2.txt", self))
        self.agents.append(Agent.fromFile("agents/agent3.txt", self))
        self.agents.append(Agent.fromFile("agents/agent4.txt", self))

        self.tradesCount = 0
        self.broadcastTradeInfo([Trade(None, None, None, None, 0, "A", 0, 0)])

    def broadcastTradeInfo(self, trades):
        for trade in trades:
            self.tradesCount = self.tradesCount + 1
            for agent in self.agents:
                self.eventQueue.queueEvent(EventMarketData(trade.timestamp + agent.latencyFunction.getLatency(), trade, agent))

    def pushEvent(self, event: Event):
        self.eventQueue.queueEvent(event)

    def run(self):
        t = time.time()
        events = 0
        while (not self.eventQueue.isEmpty()) and time.time() <= t + 10:
            events += 1
            event = self.eventQueue.nextEvent()
            print(event.toString())
            event.run()

            if events > 200:
                break
        
        print(self.orderbooks["A"].toString())

            # test to make sure this is working correctly
            # algorithms and graphing, plots at end of simulation (what are we interested in?) - things like price, volatility and relation to hypothesis
            # first blog post - talk about design, simulator



# add push event method to internally push an event (can post-process here)
# design diagram of how these classes interact with each other


# call next event, process event, which can push back