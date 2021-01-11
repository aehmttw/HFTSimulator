from events import *
from agents import *

class Simulation:
    def __init__(self):
        self.eventQueue = EventQueue(self)
        self.agents = list(Agent)

    def broadcastTradeInfo(self, trades: list('Trade')):
        for trade in trades:
            for agent in self.agents:
                self.eventQueue.queueEvent(EventMarketData(trade.time + agent.getLatency(), trade, agent))


# add push event method to internally push an event (can post-process here)
# design diagram of how these classes interact with each other


# call next event, process event, which can push back