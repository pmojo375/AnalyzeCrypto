from buy import Buy
from sell import Sell
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

class Tax:

	longterm_days = datetime.timedelta(days=365)

	longterm_2020 = 0.15
	longterm_2021 = 0.15

	shortterm_2020 = 0.24

	
	def __init__(self):
		pass


	def __str__(self):
		return "Crypto Tax Helper Class"

	def process_tax(self, sell_event):
		gains = sell_event['profit_loss']

		if sell_event['days_held'] >= self.longterm_days:
			# long term capital gain rate

			tax = round(gains * self.longterm_2020, 2)

		else:
			# short term capital gain rate

			tax = round(gains * self.shortterm_2020, 2)

		return [tax, gains]
