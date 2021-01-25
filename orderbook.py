import heapq
from order import Order
from trade import Trade
class OrderBook:
    def __init__(self, simulation: 'Simulation'):
        # Stores sell side of order book as tuples with price, timestamp, and Order.
        # The lowest sell order is popped first. In the event of a tie, the oldest one should pop first.
        self.sellbook = []

        # Stores buy side of order book as tuples with negative price, timestamp, and Order.
        # The highest buy order is popped first. In the event of a tie, the oldest one should pop first.
        self.buybook = []

        self.trades = []

        self.simulation = simulation

    # Adds an order to the order book. Used internally.
    def _addOrder(self, order: Order):
        if order.buy:
            heapq.heappush(self.buybook, (-order.price, order.timestamp, order))
        else:
            heapq.heappush(self.sellbook, (order.price, order.timestamp, order))

    def input(self, order: Order, timestamp: int):
        if order.cancel:
            for o in self.sellbook:
                order2: Order = o[2]
                if order2.orderID == order.orderID:
                    self.sellbook.remove(o)
            
            for o in self.buybook:
                order2: Order = o[2]
                if order2.orderID == order.orderID:
                    self.sellbook.remove(o)
        else:
            trades = self.matchOrder(order, timestamp)
            for trade in trades:
                trade.process() 
                self.trades.append(trade)
                
    # read config file to define latency parameters

    # Takes in an order and tries to match it
    # Create list of trade objects (buyer, seller, price, timestamp)
    def matchOrder(self, order: Order, timestamp: int) -> list:
        trades: list = list()
        if order.buy:
            if len(self.sellbook) > 0:
                while order.amount > 0:
                    other: Order = heapq.heappop(self.sellbook)[2]
                    if other.price >= order.price:
                        if other.amount > order.amount:
                            trades.append(Trade(order.agent, other.agent, order, other, other.price, order.symbol, order.amount, timestamp))
                            other.amount -= order.amount
                            order.amount = 0
                            self._addOrder(other)
                        else:
                            trades.append(Trade(order.agent, other.agent, order, other, other.price, order.symbol, other.amount, timestamp))
                            order.amount -= other.amount
                            other.amount = 0
                    else:
                        self._addOrder(order)
                        break
            else:
                self._addOrder(order)
        else:
            if len(self.buybook) > 0:
                while order.amount > 0:
                    other: Order = heapq.heappop(self.buybook)[2]
                    if other.price <= order.price:
                        if other.amount > order.amount:
                            trades.append(Trade(other.agent, order.agent, other, order, other.price, order.symbol, order.amount, order.timestamp))
                            other.amount -= order.amount
                            order.amount = 0
                            self._addOrder(other)
                        else:
                            trades.append(Trade(other.agent, order.agent, other, order, other.price, order.symbol, other.amount, order.timestamp))
                            order.amount -= other.amount
                            other.amount = 0
                    else:
                        self._addOrder(order)
                        break
            else:
                self._addOrder(order)

        self.simulation.broadcastTradeInfo(trades)
        return trades

    def print(self):
        print("Sell orders: ")
        
        for order in self.sellbook:
            o: Order = order[2]
            print("Price: " + str(o.price) + ", Quantity: " + str(o.amount))

        print("Buy orders: ")

        for order in self.buybook:
            o: Order = order[2]
            print("Price: " + str(o.price) + ", Quantity: " + str(o.amount))

