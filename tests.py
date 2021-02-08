import unittest
from simulation import Simulation
from order import Order
from orderbook import OrderBook

#python -m unittest discover
class Tests(unittest.TestCase):
    def testBuy(self):
        simulation: Simulation = Simulation()
        book: OrderBook = OrderBook(simulation)
        book.matchOrder(Order(None, True, "A", 100, 50, 0), 0)
        book.matchOrder(Order(None, True, "A", 80, 52, 0), 0)
        book.matchOrder(Order(None, True, "A", 120, 49, 0), 0)
        book.matchOrder(Order(None, True, "A", 200, 45, 0), 0)

        self.assertEqual(book._getBuyList(), [52, 80, 50, 100, 49, 120, 45, 200])
        self.assertEqual(book._getSellList(), [])

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

        self.assertEqual(book._getSellList(), [45, 200, 49, 120, 50, 100, 52, 80])
        self.assertEqual(book._getBuyList(), [])

        #Price: 45, Quantity: 200
        #Price: 49, Quantity: 120
        #Price: 50, Quantity: 100
        #Price: 52, Quantity: 80

    def testMatch(self):
        simulation: Simulation = Simulation()
        book: OrderBook = OrderBook(simulation)
        book.matchOrder(Order(None, False, "A", 100, 50, 0), 0)
        book.matchOrder(Order(None, True, "A", 100, 50, 0), 0)
        self.assertEqual(book._getBuyList(), [])
        self.assertEqual(book._getSellList(), [])

    def testPartialMatch(self):
        # Test: partially matching orders
        simulation: Simulation = Simulation()
        book: OrderBook = OrderBook(simulation)
        book.matchOrder(Order(None, False, "A", 50, 100, 0), 0)
        book.matchOrder(Order(None, True, "A", 30, 100, 0), 0)
        self.assertEqual(book._getSellList(), [100, 20])
        self.assertEqual(book._getBuyList(), [])

    def testOverflowMatch(self):
        # Test: partially matching orders
        simulation: Simulation = Simulation()
        book: OrderBook = OrderBook(simulation)
        book.matchOrder(Order(None, False, "A", 50, 100, 0), 0)
        book.matchOrder(Order(None, True, "A", 80, 100, 0), 0)
        self.assertEqual(book._getSellList(), [])
        self.assertEqual(book._getBuyList(), [100, 30])

    # test no match

    def testPerfectMultiMatch(self):
        simulation: Simulation = Simulation()
        book: OrderBook = OrderBook(simulation)
        book.matchOrder(Order(None, False, "A", 10, 100, 0), 0)
        book.matchOrder(Order(None, False, "A", 20, 100, 0), 0)
        book.matchOrder(Order(None, False, "A", 30, 100, 0), 0)
        book.matchOrder(Order(None, True, "A", 60, 100, 0), 0)
        self.assertEqual(book._getBuyList(), [])
        self.assertEqual(book._getSellList(), [])

    def testPerfectMultiMatchLeftover(self):
        simulation: Simulation = Simulation()
        book: OrderBook = OrderBook(simulation)
        book.matchOrder(Order(None, False, "A", 10, 100, 0), 0)
        book.matchOrder(Order(None, False, "A", 20, 100, 0), 0)
        book.matchOrder(Order(None, False, "A", 30, 100, 0), 0)
        book.matchOrder(Order(None, True, "A", 70, 100, 0), 0)
        self.assertEqual(book._getBuyList(), [100, 10])
        self.assertEqual(book._getSellList(), [])

    def testPerfectMultiMatchLeftover2(self):
        simulation: Simulation = Simulation()
        book: OrderBook = OrderBook(simulation)
        book.matchOrder(Order(None, False, "A", 10, 100, 0), 0)
        book.matchOrder(Order(None, False, "A", 20, 100, 0), 0)
        book.matchOrder(Order(None, False, "A", 30, 100, 0), 0)
        book.matchOrder(Order(None, True, "A", 50, 100, 0), 0)
        self.assertEqual(book._getBuyList(), [])
        self.assertEqual(book._getSellList(), [100, 10])

    def testMultiPriceMatch(self):
        simulation: Simulation = Simulation()
        book: OrderBook = OrderBook(simulation)
        book.matchOrder(Order(None, False, "A", 100, 10, 0), 0)
        book.matchOrder(Order(None, False, "A", 100, 20, 0), 0)
        book.matchOrder(Order(None, False, "A", 100, 30, 0), 0)
        book.matchOrder(Order(None, True, "A", 100, 60, 0), 0)
        self.assertEqual(book._getBuyList(), [])
        self.assertEqual(book._getSellList(), [20, 100, 30, 100])

    #make more of these