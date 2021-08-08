import unittest
from buy import Buy
from sell import Sell
from main import *
from tax import Tax
import datetime
import logging

# Create a custom logger
logger = logging.getLogger(__name__)

# Create handlers
c_handler = logging.StreamHandler()

# Create formatters and add it to handlers
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')

# Add handlers to the logger
logger.addHandler(c_handler)


class TestBuy(unittest.TestCase):
	def xtest_buy(self):
		buy = Buy("BTC", 1000, 2, datetime.datetime(2020, 4, 20))

		self.assertEqual(buy.asset, "BTC")
		self.assertEqual(buy.cost, 1000)
		self.assertEqual(buy.amount, 2)
		date = datetime.datetime(2020, 4, 20)
		self.assertEqual(buy.date, date)

class TestAll(unittest.TestCase):
	def test_all(self):
		buy = Buy("BTC", 1000, 2, datetime.datetime(2020, 4, 20))

		self.assertEqual(buy.asset, "BTC")
		self.assertEqual(buy.cost, 1000)
		self.assertEqual(buy.amount, 2)
		date = datetime.datetime(2020, 4, 20)
		self.assertEqual(buy.date, date)

class TestSell(unittest.TestCase):
	def xtest_sell(self):
		sell = Sell("BTC", 1000, 2, datetime.datetime(2020, 4, 20))

		self.assertEqual(sell.asset, "BTC")
		self.assertEqual(sell.cost, 1000)
		self.assertEqual(sell.amount, 2)
		date = datetime.datetime(2020, 4, 20)
		self.assertEqual(sell.date, date)

class TestProcess(unittest.TestCase):
	def xtest_process(self):
		buy1 = Buy("ETH", 1000, 20, datetime.datetime(2017, 1, 2)) # bought 20 ETH for $1000
		buy2 = Buy("BTC", 1000, 10, datetime.datetime(2017, 1, 1)) # bought 10 BTC for $1000
		buy3 = Buy("ETH", 1000, 10, datetime.datetime(2019, 1, 1)) # bought 10 ETH for $1000

		sell1 = Sell("BTC", 2000, 5, datetime.datetime(2019, 1, 1)) # sold 5 BTC for $2000, a $1500 profit, 0 BTC remains
		sell2 = Sell("ETH", 5000, 30, datetime.datetime(2020, 1, 1)) # sold 30 ETH for $5000, first 20 at $2333.33 profit, second at $666.66 profit, 0 ETH remains
		sell3 = Sell("BTC", 3000, 5, datetime.datetime(2018, 1, 1)) # sold 5 BTC for $3000, a $2500 profit, 5 BTC remains

		# mix up the order to test the sort feature
		buys = [buy3, buy2, buy1]
		sells = [sell1, sell2, sell3]

		data = process_history(buys, sells)

		# first value = BTC 10 buy - two tax events, first $2500 profit at long term, second $1500 profit at long term
		# second value = ETH 20 buy - $2333.33 profit long term
		# third value = ETH 10 buy - $666.66 profit long term
		taxes = []

		t = Tax()
		buys = data[0]
		sells = data[1]

		for buy in buys:
			events = buy.get_sell_events()

			log = str(len(events)) + ' sell events in ' + buy.date.strftime("%m/%d/%Y") + ' ' + buy.asset + ' buy'
			print(log)

			for event in events:
				taxes.append(t.process_tax(event))

		self.assertEqual(taxes[0], 375)
		self.assertEqual(taxes[1], 225)
		self.assertEqual(taxes[2], 350)
		self.assertEqual(taxes[3], 100)


class TestCSV(unittest.TestCase):
	def xtest_csv_buy(self):
		test_csv = ['4/7/2017', 'BUY', 'ETH', '', '21.00297962', '']
		result = csv_buy(test_csv)

		self.assertEqual(result.asset, "ETH")
		date = datetime.datetime(2017, 4, 7)
		self.assertEqual(result.date, date)
		self.assertEqual(result.og_amount, 21.00297962)

	def xtest_sell_event(self):
		test_csv_buy1 = ['4/7/2017', 'BUY', 'ETH', '', '21', '']
		test_csv_buy2 = ['4/20/2019', 'Buy', 'ETH', '', '50', '']
		test_csv_sell1 = ['4/20/2020', 'Sell', '', 'ETH', '', '18']
		test_csv_sell2 = ['4/20/2020', 'Sell', '', 'ETH', '', '5']
		buy1 = csv_buy(test_csv_buy1)
		buy2 = csv_buy(test_csv_buy2)
		sell1 = csv_sell(test_csv_sell1)
		sell2 = csv_sell(test_csv_sell2)

		self.assertEqual(buy1.sold(), False)

		remainder = buy1.sell_asset(sell1)

		sell1.buy_triggered(buy1, remainder)

		self.assertEqual(buy1.amount, 3)
		self.assertEqual(remainder, 0)
		self.assertEqual(sell1.amount, 0)

		# remainder of sell is returned
		remainder = buy1.sell_asset(sell2)

		sell2.buy_triggered(buy1, remainder)

		self.assertEqual(buy1.sold(), True)
		self.assertEqual(remainder, 2)
		self.assertEqual(sell2.amount, 2)

		remainder = buy2.sell_asset(sell2)

		sell2.buy_triggered(buy2, remainder)

		self.assertEqual(buy2.sold(), False)
		self.assertEqual(remainder, 0)
		self.assertEqual(sell2.amount, 0)

	def xtest_trade_event(self):
		test_csv_buy = ['4/7/2017', 'BUY', 'ETH', '', '21', '']
		test_csv_trade = ['4/20/2019', 'TRADE', 'BTC', 'ETH', '1', '20']

		buy = csv_buy(test_csv_buy)
		trade = csv_trade(test_csv_trade)
		trade_buy = trade[0]
		trade_sell = trade[1]

		remainder = buy.sell_asset(trade_sell)

		trade_sell.buy_triggered(buy, remainder)

		self.assertEqual(buy.amount, 1)
		self.assertEqual(remainder, 0)
		self.assertEqual(trade_sell.amount, 0)

		self.assertEqual(trade_buy.amount, 1)
