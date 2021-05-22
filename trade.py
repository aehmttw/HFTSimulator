from agents import *
from order import *

class Trade:
    def __init__(self, buyer: 'Agent', seller: 'Agent', buyOrder: 'Order', sellOrder: 'Order', price: float, symbol: str, amount: int, timestamp: float):         
        self.buyer = buyer
        self.seller = seller
        self.price = price
        self.symbol = symbol
        self.amount = amount
        self.timestamp = timestamp
        self.completed = False
        self.buyOrder = buyOrder
        self.sellOrder = sellOrder

    def process(self):
        self.buyer.shares[self.symbol] += self.amount
        self.seller.shares[self.symbol] -= self.amount
        self.buyer.balance -= self.amount * self.price
        self.seller.balance += self.amount * self.price
        self.buyer.matchedOrders += self.amount
        self.seller.matchedOrders += self.amount
        self.completed = True

        self.buyer.pricesMatched.append(self.price)
        self.seller.pricesMatched.append(self.price)
        
        self.buyer.pricesMatchedBuy.append(self.price)
        self.seller.pricesMatchedSell.append(self.price)

        if not(self.seller.groupName in self.buyer.agentsMatched):
            self.buyer.agentsMatched[self.seller.groupName] = 0

        if not(self.seller.groupName in self.buyer.agentsMatchedBuy):
            self.buyer.agentsMatchedBuy[self.seller.groupName] = 0
            self.buyer.agentPricesMatchedBuy[self.seller.groupName] = list()

        if not(self.buyer.groupName in self.seller.agentsMatched):
            self.seller.agentsMatched[self.buyer.groupName] = 0

        if not(self.buyer.groupName in self.seller.agentsMatchedSell):
            self.seller.agentsMatchedSell[self.buyer.groupName] = 0
            self.seller.agentPricesMatchedSell[self.buyer.groupName] = list()

        self.buyer.agentsMatched[self.seller.groupName] += self.amount
        self.seller.agentsMatched[self.buyer.groupName] += self.amount

        self.buyer.agentsMatchedBuy[self.seller.groupName] += self.amount
        self.seller.agentsMatchedSell[self.buyer.groupName] += self.amount
        
        self.buyer.agentPricesMatchedBuy[self.seller.groupName].append(self.price)
        self.seller.agentPricesMatchedSell[self.buyer.groupName].append(self.price)
