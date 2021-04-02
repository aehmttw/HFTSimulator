import heapq
import matplotlib.pyplot as plot
import mpl_finance as plotf
from order import Order
from trade import Trade
import numpy
class OrderBook:

    # Every agent will have their own order books, representing only the data they have received
    # These separate order books, unlike the main ones, have simulation set to None
    def __init__(self, simulation: 'Simulation', price: float, symbol: str):
        # Stores sell side of order book as tuples with price, timestamp, and Order.
        # The lowest sell order is popped first. In the event of a tie, the oldest one should pop first.
        self.sellbook = []

        # Stores buy side of order book as tuples with negative price, timestamp, and Order.
        # The highest buy order is popped first. In the event of a tie, the oldest one should pop first.
        self.buybook = []

        self.trades = []
        self.datapoints = []
        self.price = price
        self.symbol = symbol
        self.lastOrderTime = 0
        self.lastUnqueueTime = 0

        self.simulation = simulation

    # Adds an order to the order book. Used internally.
    def _addOrder(self, order: Order):      
        if order.amount <= 0:
            raise Exception("Order amount is 0!")

        #print(order.amount)

        if order.buy:
            heapq.heappush(self.buybook, (-order.price, order.receiveTimestamp, order))
        else:
            heapq.heappush(self.sellbook, (order.price, order.receiveTimestamp, order))

    def input(self, order: Order):
        #if order.cancel:
        #    print("Canceling order " + order.toString() + " / " + str(order.receiveTimestamp))
        #else:
        #if not order.cancel:
        #    print("Adding order " + order.toString() + " / " + str(order.processTimestamp))
        self.lastUnqueueTime = order.receiveTimestamp

        if order.cancel:
            success: bool = False
            for o in self.sellbook:
                order2: Order = o[2]
                if order2.orderID == order.orderID:
                    order2.agent.canceledOrders += order2.amount
                    self.sellbook.remove(o)
                    success = True
            
            for o in self.buybook:
                order2: Order = o[2]
                if order2.orderID == order.orderID:
                    order2.agent.canceledOrders += order2.amount
                    self.buybook.remove(o)
                    success = True

            #if not success:
            #    print(order.orderID)
        else:
            if order.agent is not None:
                order.agent.sentOrders += order.amount
    
            trades = self.matchOrder(order)
            for trade in trades:
                if not (self.simulation is None):
                    trade.process() 

                    #if abs(trade.price - self.price) > 10:
                    #    print(str(self.price) + " " + str(trade.price))
                    #    print(trade.buyOrder.toString())
                    #    print(trade.sellOrder.toString())

                    self.price = trade.price
                self.trades.append(trade)
            self.lastOrder = order
            self.datapoints.append(DataPoint(self, order.processTimestamp))
        #print(self.toString())

    
    def inputOrder(self, buyOrder: Order, sellOrder: Order, price: float, trades) -> bool:
        if sellOrder.price <= buyOrder.price:
            if sellOrder.amount > buyOrder.amount:
                trades.append(Trade(buyOrder.agent, sellOrder.agent, buyOrder, sellOrder, price, buyOrder.symbol, buyOrder.amount, max(buyOrder.processTimestamp, sellOrder.processTimestamp)))
                sellOrder.amount -= buyOrder.amount
                buyOrder.amount = 0

                if buyOrder.receiveTimestamp > sellOrder.receiveTimestamp:
                    self._addOrder(sellOrder)

                return buyOrder.receiveTimestamp > sellOrder.receiveTimestamp

            elif sellOrder.amount == buyOrder.amount:
                trades.append(Trade(buyOrder.agent, sellOrder.agent, buyOrder, sellOrder, price, buyOrder.symbol, buyOrder.amount, max(buyOrder.processTimestamp, sellOrder.processTimestamp)))
                sellOrder.amount = 0
                buyOrder.amount = 0

                return True
            else:
                trades.append(Trade(buyOrder.agent, sellOrder.agent, buyOrder, sellOrder, price, buyOrder.symbol, sellOrder.amount, max(buyOrder.processTimestamp, sellOrder.processTimestamp)))
                buyOrder.amount -= sellOrder.amount
                sellOrder.amount = 0

                if buyOrder.receiveTimestamp < sellOrder.receiveTimestamp:
                    self._addOrder(buyOrder)

                return buyOrder.receiveTimestamp < sellOrder.receiveTimestamp
        else:
            self._addOrder(sellOrder)
            self._addOrder(buyOrder)
            return True   
                
    # read config file to define latency parameters

    # Takes in an order and tries to match it
    # Create list of trade objects (buyer, seller, price, timestamp)
    def matchOrder(self, order: Order) -> list: # try to comment
        trades: list = list()
        if order.buy: 
            while order.amount > 0: 
                if len(self.sellbook) > 0:
                    other = heapq.heappop(self.sellbook)[2]
                    if self.inputOrder(order, other, other.price, trades):
                        break
                else:
                    self._addOrder(order)
                    break                
        else:
            while order.amount > 0:
                if len(self.buybook) > 0:
                    other = heapq.heappop(self.buybook)[2]
                    if self.inputOrder(other, order, other.price, trades):
                        break
                else:
                    self._addOrder(order)
                    break

        if not (self.simulation is None):
            self.simulation.broadcastTradeInfo(trades)
 
        return trades

    def toString(self) -> str:
        s = "Sell orders: \n"

        orders = list()
        
        while len(self.sellbook) > 0:
            order = heapq.heappop(self.sellbook)
            orders.append(order)
            o: Order = order[2]
            s += "Price: " + str(o.price) + ", Quantity: " + str(o.amount) + ", Time: " + str(o.timestamp) + " " + str(o.orderID) + "\n" 

        for order in orders:
            heapq.heappush(self.sellbook, order)

        s += "\nBuy orders: \n"

        orders = list()
        
        while len(self.buybook) > 0:
            order = heapq.heappop(self.buybook)
            orders.append(order)
            o: Order = order[2]
            s += "Price: " + str(o.price) + ", Quantity: " + str(o.amount) + ", Time: " + str(o.timestamp) + " " + str(o.orderID) + "\n"

        for order in orders:
            heapq.heappush(self.buybook, order)

        return s
    
    def toStringShort(self) -> str:
        s = "Sell orders: \n"
        
        minsell = float("inf")
        maxsell = -float("inf")

        for order in self.sellbook:
            o: Order = order[2]
            minsell = min(minsell, o.price)
            maxsell = max(maxsell, o.price)

        minbuy = float("inf")
        maxbuy = -float("inf")

        s += "Amount = " + str(len(self.sellbook)) + ", " + str(minsell) + "-" + str(maxsell)

        s += "\nBuy orders: \n"

        for order in self.buybook:
            o: Order = order[2]
            minbuy = min(minbuy, o.price)
            maxbuy = max(maxbuy, o.price)

        s += "Amount = " + str(len(self.buybook)) + ", " + str(minbuy) + "-" + str(maxbuy)

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

        gap = 0
        for datapoint in self.datapoints:
            if datapoint.gap != -1:
                gap = datapoint.gap

            times.append(datapoint.timestamp)
            data.append(gap)

        plot.figure()
        plot.xlabel("time")
        plot.ylabel("gap")
        plot.plot(times, data)   

    def plotQueueSize(self):
        times = list()
        data = list()

        for datapoint in self.datapoints:
            times.append(datapoint.timestamp)
            data.append(datapoint.queueSize)

        plot.figure()
        plot.xlabel("time")
        plot.ylabel("queue size")
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

    def plotBalances(self):
        times: list = list()
        data: dict = dict()
        
        for datapoint in self.datapoints:
            times.append(datapoint.timestamp)

            for a in datapoint.agentBalances:
                if not a.startswith("marketmaker"):
                    if not (a in data):
                        data[a] = list()

                    data[a].append(datapoint.agentBalances[a])

        plot.figure()
        plot.xlabel("time")
        plot.ylabel("balance")
        plot.legend(data)

        for a in data:
            plot.plot(times, data[a])   
    
    def plotShares(self):
        times: list = list()
        data: dict = dict()
        
        for datapoint in self.datapoints:
            times.append(datapoint.timestamp)

            for a in datapoint.agentShares:
                if not a.startswith("marketmaker"):
                    if not (a in data):
                        data[a] = list()

                    data[a].append(datapoint.agentShares[a])

        plot.figure()
        plot.xlabel("time")
        plot.ylabel("shares")
        plot.legend(data)

        for a in data:
            plot.plot(times, data[a])   

    def plotNetWorth(self):
        times: list = list()
        data: dict = dict()
        
        for datapoint in self.datapoints:
            times.append(datapoint.timestamp)

            for a in datapoint.agentShares:
                if not a.startswith("marketmaker"):
                    if not (a in data):
                        data[a] = list()

                    data[a].append(datapoint.agentShares[a] * datapoint.price + datapoint.agentBalances[a])

        plot.figure()
        plot.xlabel("time")
        plot.ylabel("net worth")
        plot.legend(data)

        for a in data:
            plot.plot(times, data[a]) 

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

    def write(self, file: str):
        f = open(file, "w")
        bar: str = "Timestamp,Price,Book Size,Gap,Volatility,Queue Size"

        for agent in self.simulation.agents:
            bar += "," + agent.name + " Cash"
        
        for agent in self.simulation.agents:
            bar += "," + agent.name + " Shares"

        for agent in self.simulation.agents:
            bar += "," + agent.name + " Orders/Sent"
        
        for agent in self.simulation.agents:
            bar += "," + agent.name + " Orders/Matched"

        for agent in self.simulation.agents:
            bar += "," + agent.name + " Orders/Canceled"

        f.write(bar + "\n")

        for datapoint in self.datapoints:
            f.write(datapoint.toCsvLine() + "\n")

        f.close()

class DataPoint:
    def __init__(self, orderBook: OrderBook, timestamp: float):
        self.price = orderBook.price
        self.timestamp = timestamp
        self.bookSize = 0
        self.queueSize = timestamp - orderBook.lastUnqueueTime
        self.agentBalances = dict()
        self.agentShares = dict()
        self.agentOrdersSent = dict()
        self.agentOrdersMatched = dict()
        self.agentOrdersCanceled = dict()

        for o in orderBook.buybook:
            self.bookSize += o[2].amount

        for o in orderBook.sellbook:
            self.bookSize += o[2].amount

        if orderBook.simulation is not None:
            for a in orderBook.simulation.agents:
                self.agentBalances[a.name] = a.balance
                self.agentShares[a.name] = a.shares[orderBook.symbol]
                self.agentOrdersSent[a.name] = a.sentOrders
                self.agentOrdersMatched[a.name] = a.matchedOrders
                self.agentOrdersCanceled[a.name] = a.canceledOrders

        if len(orderBook.sellbook) == 0 or len(orderBook.buybook) == 0:
            self.gap = -1
        else:
            s = heapq.heappop(orderBook.sellbook)
            heapq.heappush(orderBook.sellbook, s)

            b = heapq.heappop(orderBook.buybook)
            heapq.heappush(orderBook.buybook, b)

            self.gap = (s[0] + b[0])
            #if self.gap < 0:
            #    #print(orderBook.prevDesc)
            #    print(orderBook.toString())
            #    print(orderBook.lastOrder.toString())
            #    print(self.toString())
            #    print(s[2].toString())
            #    print(b[2].toString())
                #raise Exception("gap is negative")
        
        #orderBook.previousDesc = orderBook.toString()
    
    def toString(self) -> str:
        return str(self.timestamp) + " data point: price = " + str(self.price) + ", book size = " + str(self.bookSize) + ", gap = " + str(self.gap)

    def toCsvLine(self) -> str:
        s: str = str(self.timestamp) + "," + str(self.price) + "," + str(self.bookSize) + "," + str(self.gap) + "," + str(self.volatility) + "," + str(self.queueSize)

        for a in self.agentBalances:
            s += "," + str(self.agentBalances[a])

        for a in self.agentShares:
            s += "," + str(self.agentShares[a])

        for a in self.agentOrdersSent:
            s += "," + str(self.agentOrdersSent[a])

        for a in self.agentOrdersMatched:
            s += "," + str(self.agentOrdersMatched[a])

        for a in self.agentOrdersSent:
            s += "," + str(self.agentOrdersCanceled[a])

        return s

        
    
    