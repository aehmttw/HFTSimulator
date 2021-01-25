import uuid
class Order:
    # only include agent in order initially
    # submit buy or sell functions which set timestamp

    #todo - add limit support
    def __init__(self, agent: 'Agent', buy: bool, symbol: str, amount: int, price: float, timestamp: int):
        self.cancel = False
        self.orderID = uuid.uuid4()
        self.agent = agent
        self.buy = buy
        self.symbol = symbol
        self.amount = amount
        self.price = price
        self.timestamp = timestamp
    
    # A cancel order uses the same orderID as the order it is canceling

def makeCancelOrder(agent: 'Agent', cancelID: uuid, timestamp: int) -> type(Order):
    o = Order(agent, False, "", 0, 0, timestamp)
    o.cancel = True
    o.orderID = cancelID
    return o
        
