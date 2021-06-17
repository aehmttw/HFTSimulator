import heapq
import matplotlib.pyplot as plot
import mpl_finance as plotf
from order import Order
from trade import Trade
import numpy

# An OrderBook represents a stock exchange's centralized order book for a share, where all orders involving this share wait until matches can be found.
class OrderBook:
    def __init__(self, simulation: 'Simulation', price: float, symbol: str):
        # Stores sell side of order book as tuples with price (float), timestamp (float), and Order.
        # The lowest sell order is popped first. In the event of a tie, the oldest one should pop first.
        self.sellbook: list = []

        # Stores buy side of order book as tuples with negative price (float), timestamp (float), and Order.
        # The highest buy order is popped first. In the event of a tie, the oldest one should pop first.
        self.buybook: list = []

        # List of all trades transacted, stored as Trade objects
        self.trades: list = []

        # List of simulation data points, generated whenever an order is processed, stored as DataPoint objects
        self.datapoints: list = []
        self.price: float = price
        self.symbol: str = symbol

        # Time at which the newest order in the order book queue is to be processed (matched or added to the queue)
        self.lastOrderTime: float = 0

        # Time at which the last order was received and queued
        self.lastUnqueueTime: float = 0

        self.simulation: 'Simulation' = simulation

    # Adds an order to the order book. Used internally, does not try to match orders.
    def _addOrder(self, order: Order):      
        if order.amount <= 0:
            raise Exception("Order amount is 0!")

        if order.buy:
            heapq.heappush(self.buybook, (-order.price, order.receiveTimestamp, order))
        else:
            heapq.heappush(self.sellbook, (order.price, order.receiveTimestamp, order))

    # Function used to input an order into the order book, which will either match or result in the order being added
    def input(self, order: Order):
        self.lastUnqueueTime = order.receiveTimestamp

        # If the order is a cancel request, try to find the order in the order book that it's trying to cancel, and remove that order from the book
        if order.cancel:
            for o in self.sellbook:
                order2: Order = o[2]
                if order2.orderID == order.orderID:
                    order2.agent.canceledOrders += order2.amount
                    self.sellbook.remove(o)
            
            for o in self.buybook:
                order2: Order = o[2]
                if order2.orderID == order.orderID:
                    order2.agent.canceledOrders += order2.amount
                    self.buybook.remove(o)
        else:
            # The order is a regular order
            if order.agent is not None:
                order.agent.sentOrders += order.amount
    
            # Try to match the order with other orders in the order book
            trades: list = self._matchOrder(order)
            for trade in trades:
                # Process transactions (exchange of cash and shares) for all trades that were produced
                if not (self.simulation is None):
                    trade.process() 

                    # The share's market price is defined here as the last trade's price
                    self.price = trade.price

                self.trades.append(trade)

            self.lastOrder = order

            # Add a new data point whenever a new order is submitted
            self.datapoints.append(DataPoint(self, order.processTimestamp))

    # Second function involved in processing orders
    # Takes in an order and tries to match it
    # Returns list of Trade objects, describing all trades that were generated
    def _matchOrder(self, order: Order) -> list:
        trades: list = list()
        if order.buy: # If the order is a buy order, look in the sell book for things to match with
            while order.amount > 0: 
                if len(self.sellbook) > 0:
                    # Removes the "best deal" sell order from the order book, to test if it can match
                    other = heapq.heappop(self.sellbook)[2]
                    # Tries to match with the best deal. If the newly submitted order fully matches, stop looking for the next best deal.
                    if self._inputOrder(order, other, other.price, trades):
                        break
                else: # If there are no orders in the sell book, add the order to the order book
                    self._addOrder(order)
                    break                
        else: # If the order is a sell order, look in the buy book for things to match with
            while order.amount > 0:
                if len(self.buybook) > 0:
                    # Removes the "best deal" buy order from the order book, to test if it can match
                    other = heapq.heappop(self.buybook)[2]
                    # Tries to match with the best deal. If the newly submitted order fully matches, stop looking for the next best deal.
                    if self._inputOrder(other, order, other.price, trades):
                        break
                else: # If there are no orders in the buy book, add the order to the order book
                    self._addOrder(order)
                    break

        # Send information of the trade to every agent
        if not (self.simulation is None):
            self.simulation.broadcastTradeInfo(trades)
 
        return trades
    
    # Third function involved in processing orders
    # This function operates in terms of the "buy order" and "sell order" instead of the "best deal" and "newly submitted" order
    # Returns True when the newly submitted order has finished matching with the other orders to signal to stop trying to match the newly sumbitted order with other orders
    def _inputOrder(self, buyOrder: Order, sellOrder: Order, price: float, trades) -> bool:
        if sellOrder.price <= buyOrder.price: # Makes sure the best deal can actually match with the submitted order
            if sellOrder.amount > buyOrder.amount: # The buy order "runs out" first
                trades.append(Trade(buyOrder.agent, sellOrder.agent, buyOrder, sellOrder, price, buyOrder.symbol, buyOrder.amount, max(buyOrder.processTimestamp, sellOrder.processTimestamp)))
                
                # Reduce the sell order's amount by the number which matched
                sellOrder.amount -= buyOrder.amount
                # All the buy orders matched
                buyOrder.amount = 0

                # If the buy order is the newly submitted one, return the partially matched sell order to the order book (thus returning True)
                if buyOrder.receiveTimestamp > sellOrder.receiveTimestamp:
                    self._addOrder(sellOrder)

                return buyOrder.receiveTimestamp > sellOrder.receiveTimestamp
            elif sellOrder.amount == buyOrder.amount: # Both orders have perfectly match
                trades.append(Trade(buyOrder.agent, sellOrder.agent, buyOrder, sellOrder, price, buyOrder.symbol, buyOrder.amount, max(buyOrder.processTimestamp, sellOrder.processTimestamp)))
                sellOrder.amount = 0
                buyOrder.amount = 0

                # There is no more matching to do
                return True
            else: # The sell order "runs out" first
                trades.append(Trade(buyOrder.agent, sellOrder.agent, buyOrder, sellOrder, price, buyOrder.symbol, sellOrder.amount, max(buyOrder.processTimestamp, sellOrder.processTimestamp)))
                
                # Reduce the sell order's amount by the number which matched
                buyOrder.amount -= sellOrder.amount
                # All the buy orders matched
                sellOrder.amount = 0

                # If the sell order is the newly submitted one, return the partially matched sell order to the order book (thus returning True)
                if buyOrder.receiveTimestamp < sellOrder.receiveTimestamp:
                    self._addOrder(buyOrder)

                return buyOrder.receiveTimestamp < sellOrder.receiveTimestamp

        else: # If the best deal cannot match (prices are incompatible), add the best deal back to the order book (it had been removed previously), and add the submitted order too
            self._addOrder(sellOrder)
            self._addOrder(buyOrder)
            return True   

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

    # These are used for testing as an easy way to verify that the order book works as intended
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

    # Plot price over time for a simulation
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

    # Like the previous function, but uses a candlestick (open high low close) type plot, for a given time interval
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

    # Plots order book size (liquidity) over time for a simulation
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

    # Plots order book price gap (bid-ask spread) over time for a simulation. 
    # When one or more sides of the order book are empty, uses the last known gap.
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

    # Plots order book queue (how many orders are waiting due to the simulation only processing one per time unit) size over time for a simulation.
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

    # Plots volatility over time for a simulation. 
    # Must run calculateVolatility() first
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

    # Plot all agent cash over time for a simulation
    # Does not include agents whose name starts with "marketmaker"
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
    
    # Plot number of shares each agent has over time for a simulation
    # Does not include agents whose name starts with "marketmaker"
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

    # Plot net worth (# shares * value of share + total cash) each agent has over time for a simulation
    # Does not include agents whose name starts with "marketmaker"
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

    # Calculates volatility over time for prices, by calculating standard deviation of prices over the given time period
    # Stores this in a "volatility" variable in the data points
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

    # Saves the data points of the simulation to a given file in CSV format
    def write(self, file: str):
        f = open(file, "w")
        bar: str = "Timestamp,Price,Book Size,Gap,Volatility,Queue Size"

        for agent in self.simulation.agents:
            bar += ",Cash/" + agent.name
        
        for agent in self.simulation.agents:
            bar += ",Shares/" + agent.name

        for agent in self.simulation.agents:
            bar += ",Net Worth/" + agent.name

        for agent in self.simulation.agents:
            if not (agent.name.startswith("_")):
                bar += "," + agent.name + " Orders/Sent"
        
        for agent in self.simulation.agents:
            if not (agent.name.startswith("_")):
                bar += "," + agent.name + " Orders/Matched"

        for agent in self.simulation.agents:
            if not (agent.name.startswith("_")):
                bar += "," + agent.name + " Orders/Canceled"

        f.write(bar + "\n")

        for datapoint in self.datapoints:
            f.write(datapoint.toCsvLine() + "\n")

        f.close()
    
    # Saves simulation statistics to a given CSV format file
    def writeStats(self, file: str):
        f = open(file, "w")
        bar: str = "Agent,AveragePriceTraded,AveragePriceBuy,AveragePriceSell,OrdersSent,OrdersMatched,OrdersCanceled,OrdersStanding"

        #TODO fill in header 
        for agent in self.simulation.agentGroups:
            bar += "," + agent + "," + agent + "BuyCount," + agent + "BuyPrice," + agent + "SellCount," + agent + "SellPrice"; 

        f.write(bar + "\n")
        for agent in self.simulation.agents:
            f.write(agent.name + "," + str(numpy.average(agent.pricesMatched)) + "," + str(numpy.average(agent.pricesMatchedBuy)) + "," + str(numpy.average(agent.pricesMatchedSell)))
            f.write("," + str(numpy.average(agent.sentOrders)) + "," + str(numpy.average(agent.matchedOrders)) + "," + str(numpy.average(agent.canceledOrders)))

            standingOrders: int = 0

            for o in self.buybook:
                if o[2].agent == agent:
                    standingOrders += 1

            for o in self.sellbook:
                if o[2].agent == agent:
                    standingOrders += 1

            f.write("," + str(standingOrders))

            for agent2 in self.simulation.agentGroups:
                if agent2 in agent.agentsMatched:
                    f.write("," + str(agent.agentsMatched[agent2]))
                else:
                    f.write(",0")

                if agent2 in agent.agentsMatchedBuy:
                    f.write("," + str(agent.agentsMatchedBuy[agent2]) + "," + str(numpy.average(agent.agentPricesMatchedBuy[agent2])))
                else:
                    f.write(",0,0")

                if agent2 in agent.agentsMatchedSell:
                    f.write("," + str(agent.agentsMatchedSell[agent2]) + "," + str(numpy.average(agent.agentPricesMatchedSell[agent2])))
                else:
                    f.write(",0,0")


            f.write("\n")

# A data point, which represents a snapshot of the order book at given time
class DataPoint:
    def __init__(self, orderBook: OrderBook, timestamp: float):
        self.price: float = orderBook.price
        self.timestamp: float = timestamp
        self.bookSize: int = 0
        self.queueSize: int = timestamp - orderBook.lastUnqueueTime
        self.agentBalances: dict = dict()
        self.agentShares: dict = dict()
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
    
    def toString(self) -> str:
        return str(self.timestamp) + " data point: price = " + str(self.price) + ", book size = " + str(self.bookSize) + ", gap = " + str(self.gap)

    # Each data point becomes one line in a CSV file
    def toCsvLine(self) -> str:
        s: str = str(self.timestamp) + "," + str(self.price) + "," + str(self.bookSize) + "," + str(self.gap) + "," + str(self.volatility) + "," + str(self.queueSize)

        for a in self.agentBalances:
            s += "," + str(self.agentBalances[a])

        for a in self.agentShares:
            s += "," + str(self.agentShares[a])

        for a in self.agentShares:
            s += "," + str(self.agentShares[a] * self.price + self.agentBalances[a])

        for a in self.agentOrdersSent:
            if not (a.startswith("_")):
                s += "," + str(self.agentOrdersSent[a])

        for a in self.agentOrdersMatched:
            if not (a.startswith("_")):
                s += "," + str(self.agentOrdersMatched[a])

        for a in self.agentOrdersSent:
            if not (a.startswith("_")):
                s += "," + str(self.agentOrdersCanceled[a])

        return s

        
    
    