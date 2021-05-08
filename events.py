import heapq
from order import *
from orderbook import *
from agents import *

class Event:
    def __init__(self, time: float):
       self.time = time
    
    def run(self):
       pass

    def toString(self) -> str:
        return ""

    def __eq__(self, other):
        return self.time == other.time

    def __ne__(self, other):
        return self.time != other.time

    def __lt__(self, other):
        return self.time < other.time

    def __le__(self, other):
        return self.time <= other.time

    def __gt__(self, other):
        return self.time > other.time

    def __ge__(self, other):
        return self.time >= other.time

class EventOrder(Event):
    def __init__(self, time: float, order: 'Order', orderBook: 'OrderBook'):
        super().__init__(time)
        self.order = order
        self.orderBook = orderBook
        self.order.receiveTimestamp = time
        self.order.processTimestamp = time

    def run(self):
        if self.time - self.orderBook.lastOrderTime >= 1:
            self.orderBook.lastOrderTime = self.time
            self.orderBook.input(self.order)
        else:
            self.orderBook.simulation.pushEvent(EventOrderQueued(self.orderBook.lastOrderTime + 1, self))
            self.orderBook.lastOrderTime += 1

    def toString(self):
        return "Order event: time = " + str(self.time) + " from " + self.order.agent.name + "; id " + str(self.order.orderID)

class EventOrderQueued(Event):
    def __init__(self, time: float, event: EventOrder):
        super().__init__(time)
        self.event = event
        self.event.order.processTimestamp = time

    def run(self):
        self.event.orderBook.input(self.event.order)

    def toString(self):
        return "Order queued event: time = " + str(self.time) + " from " + self.order.agent.name + "; id " + str(self.order.orderID)

class EventMarketData(Event):
    def __init__(self, time: float, trade: 'Trade', target: 'Agent'):
        super().__init__(time)
        self.trade = trade
        self.target = target
    
    def run(self):
        self.target.inputData(self.trade, self.time)

    def toString(self):
        if self.trade.buyOrder is not None and self.trade.sellOrder is not None:
            return "Market data event: time = " + str(self.time) + " for " + self.target.name + "; ids " + str(self.trade.buyOrder.orderID) + ", " + str(self.trade.sellOrder.orderID) 
        else:
            return "Market data event: time = " + str(self.time) + " for " + self.target.name

class EventRequestOrderbook(Event):
    def __init__(self, time: float, agent: 'Agent', symbol: str, amount: int):
        self.agent = agent
        self.time = time
        self.symbol = symbol
        self.amount = amount

    def run(self):
        self.agent.simulation.pushEvent(EventSendOrderbook(self.time + self.agent.latencyFunction.getLatency(), self.agent, self.symbol, self.amount))

class EventSendOrderbook(Event):
    def __init__(self, time: float, agent: 'Agent', symbol: str, amount: int):
        self.agent = agent
        self.time = time
        self.symbol = symbol
        self.amount = amount
        self.lastBuyBook = list()
        self.lastSellBook = list()

        book = self.agent.simulation.orderbooks[self.symbol] 
        bb = list()
        sb = list()

        for i in range(amount):
            if len(book.buybook) > 0:
                bb.append(heapq.heappop(book.buybook))
            
            if len(book.sellbook) > 0:
                sb.append(heapq.heappop(book.sellbook))

        for o in bb:
            heapq.heappush(book.buybook, o)
            
        for o in sb:
            heapq.heappush(book.sellbook, o)

        self.lastBuyBook = bb
        self.lastSellBook = sb

    def run(self):
        self.agent.inputOrderBooks(self.time, self.lastBuyBook, self.lastSellBook)

class EventScheduleAgent(Event):
    def __init__(self, time: float, agent: 'RegularTradingAgent'):
        super().__init__(time)
        self.agent: 'RegularTradingAgent' = agent

    def run(self):
        self.agent.inputOrders(self.time)

class EventQueue:
    def __init__(self, simulation: 'Simulation'):
        self.simulation = simulation
        self.queue = list()

    def queueEvent(self, e: 'Event'):
        heapq.heappush(self.queue, e)

    def nextEvent(self) -> Event:
        return heapq.heappop(self.queue)

    def isEmpty(self) -> bool:
        return len(self.queue) == 0

# enqueue and dequeue events
# run for certain number of orders, stop and analyze
# defining event types and what to do -> api calls
# assume for now only react to trade data

# make some simple tests too

# certain types of events give market data to traders (with latency parameters) -> prompted to do stuff



# config file that has some parameters of the experiment -> read to get market data, traders

# moving average, if goes above sell or below buy take action -> one algorithm 