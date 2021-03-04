import unittest
from simulation import Simulation
from order import Order
from orderbook import OrderBook

#python -m unittest discover
class Tests(unittest.TestCase):
    def testBuy(self):
        book: OrderBook = OrderBook(None, 0)
        book.input(Order(None, True, "A", 100, 50, 0), 0)
        book.input(Order(None, True, "A", 80, 52, 0), 0)
        book.input(Order(None, True, "A", 120, 49, 0), 0)
        book.input(Order(None, True, "A", 200, 45, 0), 0)

        self.assertEqual(book._getBuyList(), [80, 52, 100, 50, 120, 49, 200, 45])
        self.assertEqual(book._getSellList(), [])

        #Price: 52, Quantity: 80
        #Price: 50, Quantity: 100
        #Price: 49, Quantity: 120
        #Price: 45, Quantity: 200

    def testSell(self):
        book: OrderBook = OrderBook(None, 0)
        book.input(Order(None, False, "A", 100, 50, 0), 0)
        book.input(Order(None, False, "A", 80, 52, 0), 0)
        book.input(Order(None, False, "A", 120, 49, 0), 0)
        book.input(Order(None, False, "A", 200, 45, 0), 0)

        self.assertEqual(book._getSellList(), [200, 45, 120, 49, 100, 50, 80, 52])
        self.assertEqual(book._getBuyList(), [])

        #Price: 45, Quantity: 200
        #Price: 49, Quantity: 120
        #Price: 50, Quantity: 100
        #Price: 52, Quantity: 80

    def testMatch(self):
        book: OrderBook = OrderBook(None, 0)
        book.input(Order(None, False, "A", 100, 50, 0), 0)
        book.input(Order(None, True, "A", 100, 50, 0), 1)
        self.assertEqual(book._getBuyList(), [])
        self.assertEqual(book._getSellList(), [])
        self.assertEqual(book._getTrades(), [100, 50])

    def testPartialMatch(self):
        # Test: partially matching orders      
        book: OrderBook = OrderBook(None, 0)
        book.input(Order(None, False, "A", 50, 100, 0), 0)
        book.input(Order(None, True, "A", 30, 100, 0), 1)
        self.assertEqual(book._getSellList(), [20, 100])
        self.assertEqual(book._getBuyList(), [])
        self.assertEqual(book._getTrades(), [30, 100])

    def testOverflowMatch(self):
        # Test: partially matching orders        
        book: OrderBook = OrderBook(None, 0)
        book.input(Order(None, False, "A", 50, 100, 0), 0)
        book.input(Order(None, True, "A", 80, 100, 0), 1)
        self.assertEqual(book._getSellList(), [])
        self.assertEqual(book._getBuyList(), [30, 100])
        self.assertEqual(book._getTrades(), [50, 100])

    def testNoMatch(self):
        # Test: no match between orders      
        book: OrderBook = OrderBook(None, 0)
        book.input(Order(None, False, "A", 50, 100, 0), 0)
        book.input(Order(None, True, "A", 80, 99, 0), 1)
        self.assertEqual(book._getSellList(), [50, 100])
        self.assertEqual(book._getBuyList(), [80, 99])

    def testPerfectMultiMatch(self): 
        book: OrderBook = OrderBook(None, 0)
        book.input(Order(None, False, "A", 10, 100, 0), 0)
        book.input(Order(None, False, "A", 20, 100, 0), 1)
        book.input(Order(None, False, "A", 30, 100, 0), 2)
        book.input(Order(None, True, "A", 60, 100, 0), 3)
        self.assertEqual(book._getBuyList(), [])
        self.assertEqual(book._getSellList(), [])
        self.assertEqual(book._getTrades(), [10, 100, 20, 100, 30, 100])

    def testPerfectMultiMatchLeftover(self):
        book: OrderBook = OrderBook(None, 0)
        book.input(Order(None, False, "A", 10, 100, 0), 0)
        book.input(Order(None, False, "A", 20, 100, 0), 1)
        book.input(Order(None, False, "A", 30, 100, 0), 2)
        book.input(Order(None, True, "A", 70, 100, 0), 3)
        self.assertEqual(book._getBuyList(), [10, 100])
        self.assertEqual(book._getSellList(), [])
        self.assertEqual(book._getTrades(), [10, 100, 20, 100, 30, 100])

    def testPerfectMultiMatchLeftover2(self):
        book: OrderBook = OrderBook(None, 0)
        book.input(Order(None, False, "A", 10, 100, 0), 0)
        book.input(Order(None, False, "A", 20, 100, 0), 0)
        book.input(Order(None, False, "A", 30, 100, 0), 0)
        book.input(Order(None, True, "A", 50, 100, 0), 0)
        self.assertEqual(book._getBuyList(), [])
        self.assertEqual(book._getSellList(), [10, 100])
        self.assertEqual(book._getTrades(), [10, 100, 20, 100, 20, 100])

    def testMultiPriceMatch(self):    
        book: OrderBook = OrderBook(None, 0)
        book.input(Order(None, False, "A", 100, 10, 0), 0)
        book.input(Order(None, False, "A", 100, 20, 0), 0)
        book.input(Order(None, False, "A", 100, 30, 0), 0)
        book.input(Order(None, True, "A", 100, 60, 0), 0)
        self.assertEqual(book._getBuyList(), [])
        self.assertEqual(book._getSellList(), [100, 20, 100, 30])
        self.assertEqual(book._getTrades(), [100, 10])

    def testMultiPriceMatch2(self):   
        book: OrderBook = OrderBook(None, 0)
        book.input(Order(None, False, "A", 100, 10, 0), 0)
        book.input(Order(None, False, "A", 100, 20, 0), 0)
        book.input(Order(None, False, "A", 100, 30, 0), 0)
        book.input(Order(None, True, "A", 150, 60, 0), 0)
        self.assertEqual(book._getBuyList(), [])
        self.assertEqual(book._getSellList(), [50, 20, 100, 30])
        self.assertEqual(book._getTrades(), [100, 10, 50, 20])

    def testMultiPriceMatch3(self):   
        book: OrderBook = OrderBook(None, 0)
        book.input(Order(None, False, "A", 100, 10, 0), 0)
        book.input(Order(None, False, "A", 100, 20, 0), 0)
        book.input(Order(None, False, "A", 100, 30, 0), 0)
        book.input(Order(None, True, "A", 150, 15, 0), 0)
        self.assertEqual(book._getBuyList(), [50, 15])
        self.assertEqual(book._getSellList(), [100, 20, 100, 30])
        self.assertEqual(book._getTrades(), [100, 10])

    #make more of these