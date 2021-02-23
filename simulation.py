from events import *
from agents import *
import time

class Simulation:
    def __init__(self):
        self.eventQueue = EventQueue(self)
        self.agents = list()
        self.orderbooks = dict()
        self.orderbooks["A"] = OrderBook(self)
        self.agents.append(AgentFixedPrice("1", self, 100, ["A"], 1, True))
        self.agents.append(AgentFixedPrice("2", self, 100, ["A"], 1, False))
        self.tradesCount = 0
        self.broadcastTradeInfo([Trade(None, None, None, None, 0, "A", 0, 0)])

    def broadcastTradeInfo(self, trades):
        for trade in trades:
            self.tradesCount = self.tradesCount + 1
            for agent in self.agents:
                self.eventQueue.queueEvent(EventMarketData(trade.timestamp + agent.getLatency(), trade, agent))

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

            if events > 20:
                break

            # test to make sure this is working correctly
            # algorithms and graphing, plots at end of simulation (what are we interested in?) - things like price, volatility and relation to hypothesis
            # first blog post - talk about design, simulator



# add push event method to internally push an event (can post-process here)
# design diagram of how these classes interact with each other


# call next event, process event, which can push back