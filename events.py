import heapq
from order import *
from orderbook import *
from agents import *

# Events are what make keep the simulation running
# They account for the "latency" part of the simulation

# Each Event has a time at which it is scheduled to happen, and an action associated with it

class Event:
    def __init__(self, time: float):
       self.time = time
    
    def run(self):
       pass

    def toString(self) -> str:
        return ""

    # Defining comparison in terms of event time
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

# An event representing an order being sent. Sent by agents and processed by the matching engine.
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

# An event signaling that an order cannot be processed directly (the matching engine only processes one order every time unit).
# The order is placed into a queue where it waits its turn to be processed by the matching engine after other orders are processed.
# Sent by the matching engine and processed by the matching engine.
class EventOrderQueued(Event):
    def __init__(self, time: float, event: EventOrder):
        super().__init__(time)
        self.event = event
        self.event.order.processTimestamp = time

    def run(self):
        self.event.orderBook.input(self.event.order)

    def toString(self):
        return "Order queued event: time = " + str(self.time) + " from " + self.order.agent.name + "; id " + str(self.order.orderID)

# An event with data from a completed trade. One EventMarketData is produced and sent to each agent for each trade.
# This is because each agent has a different latency and will receive news of the trade at a different time.
# Will be sent with an empty trade if there is no market activity, because some agents rely on this event to trigger sending orders.
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

# An event sent by the Stale Quote Arbitrage agent to request the current state of the order book.
# Amount specifies how many orders on each side of the book to send.
# When received by the matching engine, produces an EventSendOrderbook that's sent to the agent that requested it.
class EventRequestOrderbook(Event):
    def __init__(self, time: float, agent: 'Agent', symbol: str, amount: int):
        self.agent = agent
        self.time = time
        self.symbol = symbol
        self.amount = amount

    def run(self):
        self.agent.simulation.pushEvent(EventSendOrderbook(self.time + self.agent.latencyFunction.getLatency(), self.agent, self.symbol, self.amount))

# The event the matching engine sends to an agent that requested the order book, with data of the orders in the book.
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

# An event sent by an agent that is processed by that same agent.
# This is used to schedule an agent to periodically "wake up" and send orders every certain repeating time interval.
class EventScheduleAgent(Event):
    def __init__(self, time: float, agent: 'RegularTradingAgent'):
        super().__init__(time)
        self.agent: 'RegularTradingAgent' = agent

    def run(self):
        self.agent.inputOrders(self.time)

# A queue of events that a simulation has. Events are sorted by timestamp as they arrive on the queue.
# The event with the smallest time stamp is executed always.
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