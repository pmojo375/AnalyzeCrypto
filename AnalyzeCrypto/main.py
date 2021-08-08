from buy import Buy
from sell import Sell
import csv
import json
import requests
import pandas as pd
from datetime import datetime
from datetime import date as date_dm
from datetime import timedelta
import logging
import locale
locale.setlocale(locale.LC_ALL, '')  # Use '' for auto, or force e.g. to 'en_US.UTF-8'
from pathlib import Path

# Create a custom logger
logger = logging.getLogger(__name__)

headers = ['Timestamp', 'Type', 'Recieve Amount', 'Recieve Unit', 'Recieve Cost Basis', 'Recieve Unit Cost Basis', 'Send Amount', 'Send Unit', 'Send Cost Basis', 'Send Unit Cost Basis', 'Fee', 'Fee Unit', 'Sold Value', 'Sold Unit Value']

# Create handlers
c_handler = logging.StreamHandler()

# Create formatters and add it to handlers
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')

# Add handlers to the logger
logger.addHandler(c_handler)

taxes = {'2021': [], '2020': [], '2019': [], '2018': [], '2017': []}
gains = {'2021': [], '2020': [], '2019': [], '2018': [], '2017': []}

type_row = 'Type'
date_row = 'Timestamp'
buycoin_row = 'Recieve Unit'
sellcoin_row = 'Send Unit'
buycoinqty_row = 'Recieve Amount'
sellcoinqty_row = 'Send Amount'
fee_row = 'Fee'
feecoin_row = 'Fee Unit'
buyunitcost_row = 'Recieve Unit Cost Basis'
sellunitcost_row = 'Send Unit Cost Basis'
buycostbasis_row = 'Recieve Cost Basis'
sellcostbasis_row = 'Send Cost Basis'

timestamp_format = "%m/%d/%Y %H:%M:%S"
today = datetime.today()

# date limits
end2020 = datetime.strptime('12/31/2020', '%m/%d/%Y')
end2019 = datetime.strptime('12/31/2019', '%m/%d/%Y')
end2018 = datetime.strptime('12/31/2018', '%m/%d/%Y')
end2017 = datetime.strptime('12/31/2017', '%m/%d/%Y')
end2016 = datetime.strptime('12/31/2016', '%m/%d/%Y')

historical_price_base_url = 'https://min-api.cryptocompare.com/data/histoday?'
api_key = 'api_key=080fabe9260053f0c247e127847726d54deffb8117dc919a92b8e64673d9e57f'
current_price_base_url = 'https://min-api.cryptocompare.com/data/price?tsyms=USD&api_key=080fabe9260053f0c247e127847726d54deffb8117dc919a92b8e64673d9e57f&fsym='
tsym = 'tsym=USD'
limit = 'limit=1&'
fsym = 'fsym='
to_ts = 'toTs='

debit_types = ['Buy', 'Recieve', 'Air']
credit_types = ['Send']

buys = []
sells = []

coins_held = []

longterm_days = timedelta(days=365)

longterm_2020 = 0.15
longterm_2021 = 0.15

shortterm_2020 = 0.24

history_header = ['Timestamp', 'Type', 'Recieve Amount', 'Recieve Unit', 'Recieve Cost Basis', 'Recieve Unit Cost Basis', 'Send Amount', 'Send Unit', 'Send Cost Basis', 'Send Unit Cost Basis', 'Fee', 'Fee Unit']


# get list of current held coins/tokens
def get_current(assets):

	# loop through inputted assets
	for asset in assets:

		# get string length for formatting
		asset_len = len(asset)

		# print asset name in pretty format
		print(f"\n**{asset_len*'*'}**")
		print(f"* {asset} *")
		print(f"**{asset_len*'*'}**\n")

		# initialize variables
		held = 0
		realized = 0
		sold = 0
		tax = 0

		# get current price from web
		current_price_url = f'{current_price_base_url}{asset}'
		current_price_response = requests.get(current_price_url).json()

		# pull current price from web response
		asset_price = current_price_response['USD']

		# loop though buys
		for buy in buys:

			# check if buy asset is the asset in question
			if buy.asset == asset:

				if buy.amount * asset_price >= 1:

					print(f' - Added {buy.amount}')
					
					# add to asset total count
					held = buy.amount + held

		if held * asset_price >= 1:

			print(f'Asset price {asset_price}')

			print(f'Amount Held: {held} totaling {"${:,.2f}".format(asset_price * held)}')
		else:
			print('None')
		#print('Realized Gain/Loss: ')
		#print('Total Tax Owed: ')
		#print('Amount Held: ')


def add_asset(asset):
	if asset not in coins_held:
		coins_held.append(asset)


def csv_buy(row):
	asset = row[buycoin_row]
	
	add_asset(asset)

	qty = float(row[buycoinqty_row])
	timestamp = row[date_row]
	buy_cost = row[buyunitcost_row]

	asset_date = datetime.strptime(timestamp, timestamp_format)
	print(f'Importing {asset_date.strftime("%m/%d/%Y %H:%M:%S")} Importing Buy From CSV')

	if buy_cost == '':
		url = f'{historical_price_base_url}{tsym}&{fsym}{asset}&{limit}{to_ts}{asset_date.timestamp()}&{api_key}'

		r = requests.get(url)
		response = r.json()

		asset_price = response['Data'][1]['close']

		cost = asset_price
	else:
		cost = float(buy_cost)

	new_buy = Buy(asset, cost, qty, asset_date)

	return new_buy	

def csv_sell(row):
	asset = row[sellcoin_row]
	qty = float(row[sellcoinqty_row])
	timestamp = row[date_row]
	sell_cost_basis = row[sellunitcost_row]

	asset_date = datetime.strptime(timestamp, timestamp_format)
	print('Importing ' + asset_date.strftime("%m/%d/%Y %H:%M:%S") + ' Importing Sell From CSV')

	url = f'{historical_price_base_url}{tsym}&{fsym}{asset}&{limit}{to_ts}{asset_date.timestamp()}&{api_key}'

	r = requests.get(url)
	response = r.json()

	asset_price = response['Data'][1]['close']

	cost = asset_price

	new_sell = Sell(asset, cost, sell_cost_basis, qty, asset_date)

	return new_sell

def csv_trade(row):

	sell_asset = row[sellcoin_row]
	sell_qty = float(row[sellcoinqty_row])
	timestamp = row[date_row]
	sell_cost_basis = row[sellunitcost_row]

	asset_date = datetime.strptime(timestamp, timestamp_format)

	print('Importing ' + asset_date.strftime("%m/%d/%Y %H:%M:%S") + ' Trade From CSV')

	url = f'{historical_price_base_url}{tsym}&{fsym}{sell_asset}&{limit}{to_ts}{asset_date.timestamp()}&{api_key}'

	r = requests.get(url)
	response = r.json()

	sell_asset_price = response['Data'][1]['close']

	sell_cost = sell_asset_price

	new_sell = Sell(sell_asset, sell_cost, sell_cost_basis, sell_qty, asset_date)

	buy_asset = row[buycoin_row]

	add_asset(buy_asset)

	buy_qty = float(row[buycoinqty_row])
	buy_cost = row[buyunitcost_row]

	if buy_cost == '':
		url = f'{historical_price_base_url}{tsym}&{fsym}{buy_asset}&{limit}{to_ts}{asset_date.timestamp()}&{api_key}'

		r = requests.get(url)
		response = r.json()

		buy_asset_price = response['Data'][1]['close']

		buy_cost = buy_asset_price
	else:
		buy_cost = float(buy_cost)

	new_buy = Buy(buy_asset, buy_cost, buy_qty, asset_date)

	new_buy.part_of_trade(new_sell)
	new_sell.part_of_trade(new_buy)

	return [new_buy, new_sell]

def process_tax(buys):

	for buy in buys:

		print('')
		print('********************************************************************************************************')
		print(f'{buy.date.strftime("%m/%d/%Y %H:%M:%S")} BUY: {round(buy.og_amount,5)} {buy.asset} @ {"${:,.2f}".format(buy.cost)}/{buy.asset} - {"${:,.2f}".format(buy.cost*buy.og_amount)} total - {round(buy.amount, 5)} remaining')
		print('********************************************************************************************************')

		i = 1

		for event in buy.get_sell_events():
			gain = event['profit_loss']

			buy.gains.append(gains)

			if event['days_held'] >= longterm_days:
				# long term capital gain rate
				tax = round(gain * longterm_2020, 2)

			else:
				# short term capital gain rate
				tax = round(gain * shortterm_2020, 2)

			buy.tax_events.append({'gainloss': gain, 'date_bought': buy.date, 'date_sold': event['date_sold'], 'tax': tax})

			if event['trade']:
				print(f"{i} - TRADE: {event['date_sold'].strftime('%m/%d/%Y %H:%M:%S')}: {round(event['qty'],5)} {event['asset']} at {'${:,.2f}'.format(event['value'])}/{event['asset']} with a profit/loss of {'${:,.2f}'.format(gain)} and a taxable value of {'${:,.2f}'.format(tax)}")
			else:
				print(f"{i} - SELL : {event['date_sold'].strftime('%m/%d/%Y %H:%M:%S')}: {round(event['qty'],5)} {event['asset']} at {'${:,.2f}'.format(event['value'])}/{event['asset']} with a profit/loss of {'${:,.2f}'.format(gain)} and a taxable value of {'${:,.2f}'.format(tax)}")
			
			taxes[str(event['date_sold'].year)].append(tax)
			gains[str(event['date_sold'].year)].append(gain)

			i = i + 1
        

def read_csv(file_name='history.csv', buys=buys, sells=sells):

	my_file = Path("outputhistory.csv")
	if my_file.is_file():
		file_name = 'outputhistory.csv'
		with open(file_name, mode='r') as historyinput:
			reader = csv.DictReader(historyinput)

			for row in reader:
				if row[type_row] == 'Buy' or row[type_row] == 'Recieve':
					new_buy = csv_buy(row)
					buys.append(new_buy)
				if row[type_row] == 'Send':
					new_sell = csv_sell(row)
					sells.append(new_sell)
				if row[type_row] == 'Trade':
					new_trade = csv_trade(row)
					buys.append(new_trade[0])
					sells.append(new_trade[1])
	else:
		with open(file_name, mode='r') as historyinput:
			with open('outputhistory.csv', mode='w') as historyoutput:
				writer = csv.DictWriter(historyoutput, fieldnames=headers)
				reader = csv.DictReader(historyinput)

				writer.writeheader()

				rows = []

				for row in reader:
					if row[type_row] == 'Buy' or row[type_row] == 'Recieve':
						write_row = row
						new_buy = csv_buy(row)
						buys.append(new_buy)
						write_row['Sold Value'] = ''
						write_row['Sold Unit Value'] = ''
						rows.append(write_row)
					if row[type_row] == 'Send':
						write_row = row
						new_sell = csv_sell(row)
						write_row['Sold Value'] = new_sell.value * new_sell.amount
						write_row['Sold Unit Value'] = new_sell.value
						sells.append(new_sell)
						rows.append(write_row)
					if row[type_row] == 'Trade':
						write_row = row
						new_trade = csv_trade(row)
						write_row['Sold Value'] = new_trade[1].value * new_trade[1].amount
						write_row['Sold Unit Value'] = new_trade[1].value
						buys.append(new_trade[0])
						sells.append(new_trade[1])
						rows.append(write_row)

				writer.writerows(rows)

	return_data = process_history()

	buys = return_data[0]
	sells = return_data[1]

	process_tax(buys)

def process_history(buys=buys, sells=sells):

	# sort the buys and sells by date to ensure FIFO operation
	buys = sorted(buys, key=lambda item: item.date)
	sells = sorted(sells, key=lambda item: item.date)

	# iterate through the sells to process them
	for asset_sell in sells:

		# iterate through the buys to find the first available to apply the sell on
		for asset_buy in buys:

			# buy has not been depleated by sells yet and is the same coin/token
			if not asset_buy.sold() and asset_buy.asset == asset_sell.asset:

				sell_amount = asset_sell.amount

				# remaining amount of the sell to process
				remainder = asset_buy.sell_asset(asset_sell)

				# update the amount in the sell to the remainder
				asset_sell.buy_triggered(asset_buy, remainder)

				#print('Deducted ' + str(sell_amount) + ' ' + asset_sell.asset + ' from sell on ' + asset_sell.date.strftime("%m/%d/%Y") + ' from ' + asset_buy.date.strftime("%m/%d/%Y") + ' buy of ' + str(asset_buy.og_amount))

				#if asset_buy.amount > 0:
					#print(str(asset_buy.amount) + ' ' + str(asset_buy.asset) + ' remaining in buy')

				#if asset_sell.amount > 0:
					#print(str(remainder) + ' ' + str(asset_sell.asset) + ' remains in sell')

				# break out of for loop if the sell has been made completely
				if remainder == 0:
					break
	return [buys, sells]

def main():
	read_csv()
	get_current(coins_held)


if __name__ == "__main__":
    main()


	