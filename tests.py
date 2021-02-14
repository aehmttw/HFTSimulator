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

        self.assertEqual(book._getBuyList(), [80, 52, 100, 50, 120, 49, 200, 45])
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

        self.assertEqual(book._getSellList(), [200, 45, 120, 49, 100, 50, 80, 52])
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
        self.assertEqual(book._getSellList(), [20, 100])
        self.assertEqual(book._getBuyList(), [])

    def testOverflowMatch(self):
        # Test: partially matching orders
        simulation: Simulation = Simulation()
        book: OrderBook = OrderBook(simulation)
        book.matchOrder(Order(None, False, "A", 50, 100, 0), 0)
        book.matchOrder(Order(None, True, "A", 80, 100, 0), 0)
        self.assertEqual(book._getSellList(), [])
        self.assertEqual(book._getBuyList(), [30, 100])

    def testNoMatch(self):
        # Test: no match between orders
        simulation: Simulation = Simulation()
        book: OrderBook = OrderBook(simulation)
        book.matchOrder(Order(None, False, "A", 50, 100, 0), 0)
        book.matchOrder(Order(None, True, "A", 80, 99, 0), 0)
        self.assertEqual(book._getSellList(), [50, 100])
        self.assertEqual(book._getBuyList(), [80, 99])

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
        self.assertEqual(book._getBuyList(), [10, 100])
        self.assertEqual(book._getSellList(), [])

    def testPerfectMultiMatchLeftover2(self):
        simulation: Simulation = Simulation()
        book: OrderBook = OrderBook(simulation)
        book.matchOrder(Order(None, False, "A", 10, 100, 0), 0)
        book.matchOrder(Order(None, False, "A", 20, 100, 0), 0)
        book.matchOrder(Order(None, False, "A", 30, 100, 0), 0)
        book.matchOrder(Order(None, True, "A", 50, 100, 0), 0)
        self.assertEqual(book._getBuyList(), [])
        self.assertEqual(book._getSellList(), [10, 100])

    def testMultiPriceMatch(self):
        simulation: Simulation = Simulation()
        book: OrderBook = OrderBook(simulation)
        book.matchOrder(Order(None, False, "A", 100, 10, 0), 0)
        book.matchOrder(Order(None, False, "A", 100, 20, 0), 0)
        book.matchOrder(Order(None, False, "A", 100, 30, 0), 0)
        book.matchOrder(Order(None, True, "A", 100, 60, 0), 0)
        self.assertEqual(book._getBuyList(), [])
        self.assertEqual(book._getSellList(), [100, 20, 100, 30])

    def testMultiPriceMatch2(self):
        simulation: Simulation = Simulation()
        book: OrderBook = OrderBook(simulation)
        book.matchOrder(Order(None, False, "A", 100, 10, 0), 0)
        book.matchOrder(Order(None, False, "A", 100, 20, 0), 0)
        book.matchOrder(Order(None, False, "A", 100, 30, 0), 0)
        book.matchOrder(Order(None, True, "A", 150, 60, 0), 0)
        self.assertEqual(book._getBuyList(), [])
        self.assertEqual(book._getSellList(), [50, 20, 100, 30])

    def testMultiPriceMatch3(self):
        simulation: Simulation = Simulation()
        book: OrderBook = OrderBook(simulation)
        book.matchOrder(Order(None, False, "A", 100, 10, 0), 0)
        book.matchOrder(Order(None, False, "A", 100, 20, 0), 0)
        book.matchOrder(Order(None, False, "A", 100, 30, 0), 0)
        book.matchOrder(Order(None, True, "A", 150, 15, 0), 0)
        self.assertEqual(book._getBuyList(), [50, 15])
        self.assertEqual(book._getSellList(), [100, 20, 100, 30])

    #make more of these