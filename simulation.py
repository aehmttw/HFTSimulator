from events import *
from agents import *

class Simulation:
    def __init__(self):
        self.eventQueue = EventQueue(self)
        self.agents = list()
        self.orderbooks = dict()
        self.orderbooks["A"] = OrderBook(self)
        self.agents.append(AgentFixedPrice("1", 100, "A", 1, True))
        self.agents.append(AgentFixedPrice("2", 100, "A", 1, False))

    def broadcastTradeInfo(self, trades):
        for trade in trades:
            for agent in self.agents:
                self.eventQueue.queueEvent(EventMarketData(trade.time + agent.getLatency(), trade, agent))

    def pushEvent(self, event: Event):
        self.eventQueue.queueEvent(event)

    def run(self):
        while not self.eventQueue.isEmpty():
            self.eventQueue.nextEvent().run()



# add push event method to internally push an event (can post-process here)
# design diagram of how these classes interact with each other


# call next event, process event, which can push back