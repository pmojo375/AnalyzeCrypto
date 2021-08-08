import logging

# Create a custom logger
logger = logging.getLogger(__name__)

# Create handlers
c_handler = logging.StreamHandler()

# Create formatters and add it to handlers
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')

# Add handlers to the logger
logger.addHandler(c_handler)

class Buy:

	# fees are not included in the cost variable
	def __init__(self, asset, cost, amount, date, fee=0, fee_unit=''):
		self.asset = asset
		self.cost = cost
		self.date = date
		self.og_amount = amount
		self.amount = amount
		self.fee = fee
		self.fee_unit = fee_unit
		self.cost_basis = cost * amount
		self.unit_cost_basis = cost
		# sell events hold the tax information
		# when a sell happens, it triggers the sell asset on each buy if it has any remaining value and stores the information
		self.sell_events = []
		self.tax_events = []
		self.gains = []
		self.tax = []
		self.tax_events = []
		self.trade = False

	def part_of_trade(self, sell):
		self.trade_sell = sell
		self.trade = True

	def __str__(self):
		return "Bought " + amount + " " + asset + " at " + cost/amount + " per " + asset + " or " + cost + " total with a " + fee + " " + fee_unit + " fee"

	def sold(self):
		if self.amount > 0:
			return False
		else:
			return True

	# subtracts a sell from the amount and returns the remainder of the sell if there is any or 0
	def sell_asset(self, sell):
		return_value = 0

		if sell.amount >= self.amount:
			return_value = sell.amount - self.amount
			
			self.sell_event(sell.asset, self.amount, sell.value, sell.unit_cost_basis, sell.date, sell.trade)

			self.amount = 0

		else:
			self.amount = self.amount - sell.amount

			self.sell_event(sell.asset, sell.amount, sell.value, sell.unit_cost_basis, sell.date, sell.trade)

		return return_value

	# creates a sell even dict that holds the sale information tied to this buy
	# returns this information to the caller (most likely the sell so it can store the data too)
	def sell_event(self, asset, amount_sold, value, unit_cost_basis, date_sold, trade):



		sell_event = {'trade': trade, 'asset': asset, 'date_sold': date_sold, 'qty': amount_sold, 'unit_cost_basis': unit_cost_basis, 'value': value, 'profit_loss': round((value - unit_cost_basis) * amount_sold, 2), 'days_held': date_sold - self.date}
		self.sell_events.append(sell_event)

		return sell_event

	def get_sell_events(self):
		return self.sell_events










