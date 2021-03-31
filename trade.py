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

