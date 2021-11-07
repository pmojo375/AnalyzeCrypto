class Buy:

	# fees are not included in the cost variable
	def __init__(self, asset, unit_cost, amount, timestamp, fee=0, fee_unit=''):
		self.asset = asset # the asset being bought
		self.timestamp = timestamp # the timestamp of the event
		self.og_amount = float(amount) # the amount bought at the time of purchase
		self.amount = float(amount) # holds the amount to pull from for tax calculation purposes
		self.fee = fee # purchase fee
		self.fee_unit = fee_unit # the fee's unit
		self.unit_cost_basis = float(unit_cost) # the assets unit cost at the time of purchase i.e. cost per unit of crypto bought in USD
		self.cost_basis = self.unit_cost_basis * self.og_amount # the total cost basis which is the unit cost multiplied by the amount bought i.e 56.7 ETH for $10,000
		# sell events hold the tax information
		# when a sell happens, it triggers the sell asset on each buy if it has any remaining value and stores the information
		self.sell_events = []
		self.tax_events = []
		self.gains = []
		self.tax = []
		self.tax_events = []
		self.trade = False

	# this method is called when the buy was triggered as part of a trade.
	# a trade 15 ETH recieved for 2 BTC would call this on the ETH recieved buy object
	def part_of_trade(self, sell):
		self.trade_sell = sell
		self.trade = True

	# returns a string with a string with the objects basic information
	def __str__(self):
		return f'Bought {self.og_amount} {self.asset} at {self.unit_cost} per {self.asset} or {self.cost_basis} total with a {self.fee} {self.fee_unit} fee'

	# returns true if the buy object is depleated when calculating tax data
	def is_sold(self):
		if self.amount > 0:
			return False
		else:
			return True

	# subtracts a sell from the amount and returns the remainder of the sell if there is any or 0
	def sell_asset(self, sell):

		# the amount remaining of the sell if it wasnt able to be fully processed from this buy
		return_value = 0

		# if the amount being sold is more than the amount of the buy remaining
		if sell.amount >= self.amount:

			# update the return value
			return_value = sell.amount - self.amount
			
			# add the sell event to the list of the buys' sell events
			self.sell_event(sell.asset, self.amount, sell.cost_basis, sell.unit_cost_basis, sell.timestamp, sell.trade)

			# set the buys remaining amount to zero
			self.amount = 0

		else:
			self.amount = self.amount - sell.amount

			self.sell_event(sell.asset, sell.amount, sell.cost_basis, sell.unit_cost_basis, sell.timestamp, sell.trade)

		return return_value

	# creates a sell event dict that holds the sale information tied to this buy
	# returns this information to the caller (most likely the sell so it can store the data too)
	def sell_event(self, asset, amount_sold, sell_cost_basis, sell_unit_cost_basis, timestamp, trade):

		sell_event = {'trade': trade,
					  'asset': asset,
					  'timestamp': timestamp,
					  'qty': amount_sold,
					  'unit_cost_basis': sell_unit_cost_basis,
					  'cost_basis': sell_cost_basis,
					  'profit_loss': round((sell_unit_cost_basis - self.unit_cost_basis) * amount_sold, 2),
					  'days_held': timestamp - self.timestamp}

		self.sell_events.append(sell_event)

		return sell_event

	def get_sell_events(self):
		return self.sell_events










