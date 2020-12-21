import uuid

class Order:
    # only include agent in order initially
    # submit buy or sell functions which set timestamp
    def __init__(self, agent, buy, limit, symbol, amount, price, timestamp):
        self.cancel = False
        self.orderID = uuid.uuid4()
        self.agent = agent
        self.buy = buy
        self.limit = limit
        self.symbol = symbol
        self.amount = amount
        self.price = price
        self.timestamp = timestamp
    
    # A cancel order uses the same orderID as the order it is canceling
    def makeCancelOrder(self, agent, cancelID, timestamp):
        o = Order(agent, False, False, "", 0, 0, timestamp)
        o.cancel = True
        o.orderID = cancelID
        return o
        
