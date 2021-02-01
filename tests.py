import unittest
from simulation import Simulation
from order import Order
from orderbook import OrderBook

class Tests(unittest.TestCase):

    def testBuy(self):
        simulation: Simulation = Simulation()
        book: OrderBook = OrderBook(simulation)
        book.matchOrder(Order(None, True, "A", 100, 50, 0), 0)
        book.matchOrder(Order(None, True, "A", 80, 52, 0), 0)
        book.matchOrder(Order(None, True, "A", 120, 49, 0), 0)
        book.matchOrder(Order(None, True, "A", 200, 45, 0), 0)

        l = book.getBuyList()
        self.assertTrue(l == [52, 80, 50, 100, 49, 120, 45, 200])

        #Price: 52, Quantity: 80
        #Price: 50, Quantity: 100
        #Price: 49, Quantity: 120
        #Price: 45, Quantity: 200

    def testSell(self):
        simulation: Simulation = Simulation()
        book: OrderBook = OrderBook(simulation)
        book.matchOrder(Order(None, False, "A", 100, 50, 0), 0)
        book.matchOrder(Order(None, False, "A", 80, 52, 0), 0)
        book.matchOrder(Order(None, False, "A", 120, 49, 0), 0)
        book.matchOrder(Order(None, False, "A", 200, 45, 0), 0)
        self.assertTrue(l == [45, 200, 49, 120, 50, 100, 52, 80])

        #Price: 45, Quantity: 200
        #Price: 49, Quantity: 120
        #Price: 50, Quantity: 100
        #Price: 52, Quantity: 80
