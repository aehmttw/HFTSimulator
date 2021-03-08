import heapq
import matplotlib.pyplot as plot
import mpl_finance as plotf
from order import Order
from trade import Trade
import numpy
class OrderBook:

    # Every agent will have their own order books, representing only the data they have received
    # These separate order books, unlike the main ones, have simulation set to None
    def __init__(self, simulation: 'Simulation', price: float):
        # Stores sell side of order book as tuples with price, timestamp, and Order.
        # The lowest sell order is popped first. In the event of a tie, the oldest one should pop first.
        self.sellbook = []

        # Stores buy side of order book as tuples with negative price, timestamp, and Order.
        # The highest buy order is popped first. In the event of a tie, the oldest one should pop first.
        self.buybook = []

        self.trades = []
        self.datapoints = []
        self.price = price

        self.simulation = simulation

    # Adds an order to the order book. Used internally.
    def _addOrder(self, order: Order, timestamp: float):
        if order.buy:
            heapq.heappush(self.buybook, (-order.price, timestamp, order))
        else:
            heapq.heappush(self.sellbook, (order.price, timestamp, order))

    def input(self, order: Order, timestamp: float):
        if order.cancel:
            for o in self.sellbook:
                order2: Order = o[2]
                if order2.orderID == order.orderID:
                    self.sellbook.remove(o)
            
            for o in self.buybook:
                order2: Order = o[2]
                if order2.orderID == order.orderID:
                    self.buybook.remove(o)
        else:
            trades = self.matchOrder(order, timestamp)
            for trade in trades:
                if not (self.simulation is None):
                    trade.process() 
                    self.price = trade.price
                self.trades.append(trade)
            self.datapoints.append(DataPoint(self, timestamp))

    
    def inputOrder(self, order1: Order, order2: Order, price: float, timestamp: float, trades) -> bool:
        if order2.price <= order1.price:
            if order2.amount > order1.amount:
                trades.append(Trade(order1.agent, order2.agent, order1, order2, price, order1.symbol, order1.amount, timestamp))
                order2.amount -= order1.amount
                order1.amount = 0
                self._addOrder(order2, timestamp)
                return True
            else:
                trades.append(Trade(order1.agent, order2.agent, order1, order2, price, order1.symbol, order2.amount, timestamp))
                order1.amount -= order2.amount
                order2.amount = 0
                return False
        else:
            self._addOrder(order2, timestamp)
            self._addOrder(order1, timestamp)
            return True   
                
    # read config file to define latency parameters

    # Takes in an order and tries to match it
    # Create list of trade objects (buyer, seller, price, timestamp)
    def matchOrder(self, order: Order, timestamp: float) -> list: # try to comment
        trades: list = list()
        if order.buy: 
            while order.amount > 0: 
                if len(self.sellbook) > 0:
                    other = heapq.heappop(self.sellbook)[2]
                    if self.inputOrder(order, other, other.price, timestamp, trades):
                        break
                else:
                    self._addOrder(order, timestamp)
                    break                
        else:
            while order.amount > 0:
                if len(self.buybook) > 0:
                    other = heapq.heappop(self.buybook)[2]
                    if self.inputOrder(other, order, other.price, timestamp, trades):
                        break
                else:
                    self._addOrder(order, timestamp)
                    break

        if not (self.simulation is None):
            self.simulation.broadcastTradeInfo(trades)
 
        return trades

    def toString(self) -> str:
        s = "Sell orders: \n"
        
        for order in self.sellbook:
            o: Order = order[2]
            s += "Price: " + str(o.price) + ", Quantity: " + str(o.amount) + "\n"

        s += "\nBuy orders: \n"

        for order in self.buybook:
            o: Order = order[2]
            s += "Price: " + str(o.price) + ", Quantity: " + str(o.amount) + "\n"
        
        return s

    def _getBuyList(self) -> list:
        l = list()
        for order in self.buybook:
            o = order[2]
            l.append(o.amount)
            l.append(o.price)
        return l

    def _getSellList(self) -> list:
        l = list()
        for order in self.sellbook:
            o = order[2]
            l.append(o.amount)
            l.append(o.price)
        return l

    def _getTrades(self) -> list:
        l = list()
        for trade in self.trades:
            l.append(trade.amount)
            l.append(trade.price)
        return l

    def plotPrice(self):
        times = list()
        data = list()

        for datapoint in self.datapoints:
            times.append(datapoint.timestamp)
            data.append(datapoint.price)

        plot.figure()
        plot.xlabel("time")
        plot.ylabel("price")
        plot.plot(times, data)   
        #plotf.candlestick_ohlc(times, data, width=25)

    def plotPriceCandlestick(self, interval: float):
        data = list()

        last: int = 0

        start: float = -1
        current: float = 0
        low: float = current
        high: float = current

        for datapoint in self.datapoints:
            if start < 0:
                start = datapoint.price
                current = datapoint.price
                low = datapoint.price
                high = datapoint.price

            l = int((datapoint.timestamp) / interval)

            if l > last:
                data.append((l * interval, start, high, low, current))
                start = current
                low = current
                high = current
                last = l

            current = datapoint.price
            low = min(datapoint.price, low)
            high = max(datapoint.price, high)

        fig, ax = plot.subplots()

        plot.figure()
        ax.set_xlabel('time')
        ax.set_ylabel('price')
        plotf.candlestick_ohlc(ax, data)   

    def plotBookSize(self):
        times = list()
        data = list()

        for datapoint in self.datapoints:
            times.append(datapoint.timestamp)
            data.append(datapoint.bookSize)

        plot.figure()
        plot.xlabel("time")
        plot.ylabel("book size")
        plot.plot(times, data)   

    def plotGap(self):
        times = list()
        data = list()

        for datapoint in self.datapoints:
            times.append(datapoint.timestamp)
            data.append(datapoint.gap)

        plot.figure()
        plot.xlabel("time")
        plot.ylabel("gap")
        plot.plot(times, data)   

    def plotVolatility(self):
        times = list()
        data = list()
        
        for datapoint in self.datapoints:
            times.append(datapoint.timestamp)
            data.append(datapoint.volatility)

        plot.figure()
        plot.xlabel("time")
        plot.ylabel("volatility")
        plot.plot(times, data)   

    def calculateVolatility(self, time: float):
        index: int = 0
        for datapoint in self.datapoints:
            price = list()

            index2: int = index
            while index2 >= 0:
                time2: float = self.datapoints[index2].timestamp

                if time2 + time >= datapoint.timestamp:
                    price.append(self.datapoints[index2].price)
                    index2 -= 1
                else:
                    break
            
            datapoint.volatility = numpy.std(price)
            index += 1

class DataPoint:
    def __init__(self, orderBook: OrderBook, timestamp: float):
        self.price = orderBook.price
        self.timestamp = timestamp
        self.bookSize = len(orderBook.sellbook) + len(orderBook.buybook)

        if len(orderBook.sellbook) == 0 or len(orderBook.buybook) == 0:
            self.gap = -1
        else:
            s = heapq.heappop(orderBook.sellbook)
            heapq.heappush(orderBook.sellbook, s)

            b = heapq.heappop(orderBook.buybook)
            heapq.heappush(orderBook.buybook, b)

            self.gap = (s[0] + b[0])
    
    def toString(self) -> str:
        return str(self.timestamp) + " data point: price = " + str(self.price) + ", book size = " + str(self.bookSize) + ", gap = " + str(self.gap)

        
    
    