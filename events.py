import heapq
from order import *
from orderbook import *
from agents import *

class Event:
    def __init__(self, time: float):
       self.time = time
    
    def run(self):
       pass

class EventOrder(Event):
    def __init__(self, time: float, order: Order, orderBook: OrderBook):
        super.__init__(self, time)
        self.order = order
        self.orderBook = orderBook
    
    def run(self):
        self.orderBook.input(self.order, self.time)
class EventMarketData(Event):
    def __init__(self, time: float, trade: Trade, target: Agent):
        super.__init__(self, time)
        self.trade = trade
        self.target = target
    
    def run(self):
        self.target.inputData(self.trade)

class EventQueue:
    def __init__(self, simulation: 'Simulation'):
        self.simulation = simulation
        self.queue = list()

    def queueEvent(self, e: Event):
        heapq.heappush(self.queue, (e.time, e))

    def nextEvent(self) -> Event:
        return heapq.heappop(self.queue)(1)

# enqueue and dequeue events
# run for certain number of orders, stop and analyze
# defining event types and what to do -> api calls
# assume for now only react to trade data

# make some simple tests too

# certain types of events give market data to traders (with latency parameters) -> prompted to do stuff



# config file that has some parameters of the experiment -> read to get market data, traders

# moving average, if goes above sell or below buy take action -> one algorithm 