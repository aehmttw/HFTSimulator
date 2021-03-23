import uuid
class Order:
    # only include agent in order initially
    # submit buy or sell functions which set timestamp

    #todo - add limit support
    def __init__(self, agent: 'Agent', buy: bool, symbol: str, amount: int, price: float, timestamp: float):
        self.cancel = False
        self.orderID = uuid.uuid4()
        self.agent = agent
        self.buy = buy
        self.symbol = symbol
        self.amount = amount
        self.price = price
        self.timestamp = timestamp
        self.receiveTimestamp = timestamp
        self.processTimestamp = timestamp
    
    # A cancel order uses the same orderID as the order it is canceling

    def __eq__(self, other):
        return self.orderID == other.orderID

    def __ne__(self, other):
        return self.orderID != other.orderID

    def __lt__(self, other):
        return self.orderID < other.orderID

    def __le__(self, other):
        return self.orderID <= other.orderID

    def __gt__(self, other):
        return self.orderID > other.orderID

    def __ge__(self, other):
        return self.orderID >= other.orderID

    def toString(self):
        if self.agent is None:
            return "agent = None, buy = " + str(self.buy) + ", amount = " + str(self.amount) + ", price = " + str(self.price) + ", time = " + str(self.timestamp)
        else:
            return "agent = " + self.agent.name + ", buy = " + str(self.buy) + ", amount = " + str(self.amount) + ", price = " + str(self.price) + ", time = " + str(self.timestamp)
