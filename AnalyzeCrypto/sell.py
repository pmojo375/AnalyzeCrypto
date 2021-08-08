import logging\

# Create a custom logger
logger = logging.getLogger(__name__)

# Create handlers
c_handler = logging.StreamHandler()

# Create formatters and add it to handlers
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')

# Add handlers to the logger
logger.addHandler(c_handler)

class Sell:

	sell_events = []
	buys_decremented = []
	taxs = []

	def __init__(self, asset, cost, cost_basis, amount, date, fee=0, fee_unit=''):
		self.asset = asset
		self.cost = cost
		self.date = date
		self.amount = amount
		self.og_amount = amount
		self.fee = fee
		self.fee_unit = fee_unit
		self.unit_cost_basis = float(cost_basis)
		self.value = cost
		self.cost_basis = float(cost_basis) * amount
		self.trade = False

	# fix cost since its now the cost basis
	def __str__(self):
		return "Sold " + amount + " " + asset + " at " + unit_value + " per " + asset + " at " + cost + " total"

	def part_of_trade(self, buy):
		self.trade = True
		self.trade_buy = buy

	def buy_triggered(self, buy, remainder):
		self.buys_decremented.append(buy)
		self.amount = remainder

	def sell_event(self, sell_event):
		self.sell_events.append(sell_event)