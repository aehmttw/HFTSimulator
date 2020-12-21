import heapq


class OrderBook:
    def __init__(self):
        # Stores sell side of order book as tuples with price, timestamp, and Order.
        # The lowest sell order is popped first. In the event of a tie, the oldest one should pop first.
        self.sellbook = []

        # Stores buy side of order book as tuples with negative price, timestamp, and Order.
        # The highest buy order is popped first. In the event of a tie, the oldest one should pop first.
        self.buybook = []

    # Adds an order to the order book. Used internally.
    def _addOrder(self, order):
        if order.buy:
            heapq.heappush(self.buybook, (-order.price, order.timestamp, order))
        else:
            heapq.heappush(self.sellbook, (order.price, order.timestamp, order))

    # Takes in an order and tries to match it
    # Create list of trade objects (buyer, seller, price, timestamp)
    def matchOrder(self, order):
        if order.buy:
            other = heapq.heappop(self.sellbook)

            if other[0] <= order.price:
                # match
                pass
        else:
            pass
            # todo
