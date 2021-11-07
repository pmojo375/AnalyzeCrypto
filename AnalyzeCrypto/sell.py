class Sell:

	sell_events = []
	buys_decremented = []
	taxs = []

	def __init__(self, asset, unit_cost_basis, amount, timestamp, fee=0, fee_unit=''):
		self.asset = asset # the asset being sold
		self.timestamp = timestamp # the timestamp of the event
		self.og_amount = float(amount) # the amount being sold at the time of the sell
		self.amount = self.og_amount # the amount remaining from the sell object when calculating events
		self.fee = fee # the fee for the sell event
		self.fee_unit = fee_unit # the fees unit
		self.unit_cost_basis = float(unit_cost_basis) # the value of the sell in USD per unit sold
		self.cost_basis = self.unit_cost_basis * self.og_amount # the total value of the sell in USD
		self.trade = False # designates that the sell was part of a trade event

	# fix cost since its now the cost basis
	def __str__(self):
		return f'Sold {self.og_amount} {self.asset} at {self.unit_cost_basis} per {self.asset} or {self.cost_basis} total with a fee of {self.fee} {self.fee_unit}'

	# called when the sell was part of a trade and flags it as one
	def part_of_trade(self, buy):
		self.trade = True
		self.trade_buy = buy


	def buy_triggered(self, buy, remainder):
		self.buys_decremented.append(buy)
		self.amount = remainder

	# stores the sell event 
	def sell_event(self, sell_event):
		self.sell_events.append(sell_event)