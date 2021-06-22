import unittest
from simulation import Simulation
from order import Order
from orderbook import OrderBook

# Tests to verify the matching engine is working correctly

#python -m unittest discover
class Tests(unittest.TestCase):
    def testBuy(self):
        book: OrderBook = OrderBook(None, 0, "A")
        book.input(Order(None, True, "A", 100, 50, 1))
        book.input(Order(None, True, "A", 80, 52, 2))
        book.input(Order(None, True, "A", 120, 49, 3))
        book.input(Order(None, True, "A", 200, 45, 4))

        self.assertEqual(book._getBuyList(), [80, 52, 100, 50, 120, 49, 200, 45])
        self.assertEqual(book._getSellList(), [])

    def testSell(self):
        book: OrderBook = OrderBook(None, 0, "A")
        book.input(Order(None, False, "A", 100, 50, 1))
        book.input(Order(None, False, "A", 80, 52, 2))
        book.input(Order(None, False, "A", 120, 49, 3))
        book.input(Order(None, False, "A", 200, 45, 4))

        self.assertEqual(book._getSellList(), [200, 45, 120, 49, 100, 50, 80, 52])
        self.assertEqual(book._getBuyList(), [])

    def testMatch(self):
        book: OrderBook = OrderBook(None, 0, "A")
        book.input(Order(None, False, "A", 100, 50, 1))
        book.input(Order(None, True, "A", 100, 50, 2))
        self.assertEqual(book._getBuyList(), [])
        self.assertEqual(book._getSellList(), [])
        self.assertEqual(book._getTrades(), [100, 50])

    def testPartialMatch(self):
        # Test: partially matching orders      
        book: OrderBook = OrderBook(None, 0, "A")
        book.input(Order(None, False, "A", 50, 100, 1))
        book.input(Order(None, True, "A", 30, 100, 2))
        self.assertEqual(book._getSellList(), [20, 100])
        self.assertEqual(book._getBuyList(), [])
        self.assertEqual(book._getTrades(), [30, 100])

    def testOverflowMatch(self):
        # Test: partially matching orders        
        book: OrderBook = OrderBook(None, 0, "A")
        book.input(Order(None, False, "A", 50, 100, 1))
        book.input(Order(None, True, "A", 80, 100, 2))
        self.assertEqual(book._getSellList(), [])
        self.assertEqual(book._getBuyList(), [30, 100])
        self.assertEqual(book._getTrades(), [50, 100])

    def testNoMatch(self):
        # Test: no match between orders      
        book: OrderBook = OrderBook(None, 0, "A")
        book.input(Order(None, False, "A", 50, 100, 1))
        book.input(Order(None, True, "A", 80, 99, 2))
        self.assertEqual(book._getSellList(), [50, 100])
        self.assertEqual(book._getBuyList(), [80, 99])

    def testPerfectMultiMatch(self): 
        book: OrderBook = OrderBook(None, 0, "A")
        book.input(Order(None, False, "A", 10, 100, 1))
        book.input(Order(None, False, "A", 20, 100, 2))
        book.input(Order(None, False, "A", 30, 100, 3))
        book.input(Order(None, True, "A", 60, 100, 4))
        self.assertEqual(book._getBuyList(), [])
        self.assertEqual(book._getSellList(), [])
        self.assertEqual(book._getTrades(), [10, 100, 20, 100, 30, 100])

    def testPerfectMultiMatchLeftover(self):
        book: OrderBook = OrderBook(None, 0, "A")
        book.input(Order(None, False, "A", 10, 100, 1))
        book.input(Order(None, False, "A", 20, 100, 2))
        book.input(Order(None, False, "A", 30, 100, 3))
        book.input(Order(None, True, "A", 70, 100, 4))
        self.assertEqual(book._getBuyList(), [10, 100])
        self.assertEqual(book._getSellList(), [])
        self.assertEqual(book._getTrades(), [10, 100, 20, 100, 30, 100])

    def testPerfectMultiMatchLeftover2(self):
        book: OrderBook = OrderBook(None, 0, "A")
        book.input(Order(None, False, "A", 10, 100, 1))
        book.input(Order(None, False, "A", 20, 100, 2))
        book.input(Order(None, False, "A", 30, 100, 3))
        book.input(Order(None, True, "A", 50, 100, 4))
        self.assertEqual(book._getBuyList(), [])
        self.assertEqual(book._getSellList(), [10, 100])
        self.assertEqual(book._getTrades(), [10, 100, 20, 100, 20, 100])

    def testMultiPriceMatch(self):    
        book: OrderBook = OrderBook(None, 0, "A")
        book.input(Order(None, False, "A", 100, 10, 1))
        book.input(Order(None, False, "A", 100, 20, 2))
        book.input(Order(None, False, "A", 100, 30, 3))
        book.input(Order(None, True, "A", 100, 60, 4))
        self.assertEqual(book._getBuyList(), [])
        self.assertEqual(book._getSellList(), [100, 20, 100, 30])
        self.assertEqual(book._getTrades(), [100, 10])

    def testMultiPriceMatch2(self):   
        book: OrderBook = OrderBook(None, 0, "A")
        book.input(Order(None, False, "A", 100, 10, 1))
        book.input(Order(None, False, "A", 100, 20, 2))
        book.input(Order(None, False, "A", 100, 30, 3))
        book.input(Order(None, True, "A", 150, 60, 4))
        self.assertEqual(book._getBuyList(), [])
        self.assertEqual(book._getSellList(), [50, 20, 100, 30])
        self.assertEqual(book._getTrades(), [100, 10, 50, 20])

    def testMultiPriceMatch3(self):   
        book: OrderBook = OrderBook(None, 0, "A")
        book.input(Order(None, False, "A", 100, 10, 1))
        book.input(Order(None, False, "A", 100, 20, 2))
        book.input(Order(None, False, "A", 100, 30, 3))
        book.input(Order(None, True, "A", 150, 15, 4))
        self.assertEqual(book._getBuyList(), [50, 15])
        self.assertEqual(book._getSellList(), [100, 20, 100, 30])
        self.assertEqual(book._getTrades(), [100, 10])

    def testPartialInverseMatch(self):    
        book: OrderBook = OrderBook(None, 0, "A")
        book.input(Order(None, True, "A", 60, 100, 1))
        book.input(Order(None, False, "A", 10, 100, 2))
        self.assertEqual(book._getBuyList(), [50, 100])
        self.assertEqual(book._getSellList(), [])
        self.assertEqual(book._getTrades(), [10, 100])

    def testPartialMultiMatch(self):    
        book: OrderBook = OrderBook(None, 0, "A")
        book.input(Order(None, True, "A", 60, 100, 1))
        book.input(Order(None, False, "A", 10, 100, 2))
        book.input(Order(None, False, "A", 20, 90, 3))
        book.input(Order(None, False, "A", 35, 80, 4))
        self.assertEqual(book._getBuyList(), [])
        self.assertEqual(book._getSellList(), [5, 80])
        self.assertEqual(book._getTrades(), [10, 100, 20, 100, 30, 100])

    def testPartialMultiMatch2(self):    
        book: OrderBook = OrderBook(None, 0, "A")
        book.input(Order(None, False, "A", 10, 100, 1))
        book.input(Order(None, False, "A", 20, 90, 2))
        book.input(Order(None, False, "A", 35, 80, 3))
        book.input(Order(None, True, "A", 60, 100, 4))
        self.assertEqual(book._getBuyList(), [])
        self.assertEqual(book._getSellList(), [5, 100])
        self.assertEqual(book._getTrades(), [35, 80, 20, 90, 5, 100])

    #make more of these