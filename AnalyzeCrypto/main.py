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

headers = ['Timestamp', 'Type', 'Recieve Amount', 'Recieve Unit', 'Recieve Cost Basis', 'Recieve Unit Cost Basis', 'Send Amount', 'Send Unit', 'Send Cost Basis', 'Send Unit Cost Basis', 'Fee', 'Fee Unit', 'Sold Value', 'Sold Unit Value']

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
buyunitcost_row = 'Recieve Unit Cost Basis' # USD value of assets per unit worth
sellunitcost_row = 'Send Unit Cost Basis' # USD value of assets per unit worth
buycostbasis_row = 'Recieve Cost Basis' # USD amount the event was worth
sellcostbasis_row = 'Send Cost Basis' # USD amount the event was worth

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
def get_current(assets, buys):

	return_data = {}
	assets_list = []
	amount = {}
	rates = {}

	# loop through inputted assets
	for asset in assets:

		# initialize variables
		held = 0
		realized = 0
		sold = 0
		tax = 0
		print(asset)
		# get current price from web
		current_price_url = f'{current_price_base_url}{asset}'
		current_price_response = requests.get(current_price_url).json()

		if 'USD' in current_price_response:
			# pull current price from web response
			asset_price = current_price_response['USD']
		else:
			asset_price = 0

		# loop though buys
		for buy in buys:

			# check if buy asset is the asset in question
			if buy.asset == asset:

				# add to asset total count
				held = buy.amount + held

		amount[asset] = held
		assets_list.append(asset)
		rates[asset] = asset_price

	return_data['amount'] = amount
	return_data['assets'] = assets_list
	return_data['rates'] = rates

	return return_data


# adds the asset to a unique list of all coins that have been either bought, sold or traded
def add_asset(asset):
	if asset not in coins_held:
		coins_held.append(asset)


def csv_buy(row):

	# get the asset
	asset = row[buycoin_row]

	# add asset to list of assets
	add_asset(asset)

	# get the quantity
	qty = float(row[buycoinqty_row])

	# get the timestamp and print
	timestamp = datetime.strptime(row[date_row], timestamp_format)

	print(f'Importing {timestamp.strftime("%m/%d/%Y %H:%M:%S")} Importing Buy From CSV')

	# if there is no unit cost then get it from an API
	if row[buyunitcost_row] == '':
		url = f'{historical_price_base_url}{tsym}&{fsym}{asset}&{limit}{to_ts}{timestamp.timestamp()}&{api_key}'

		unit_cost_basis = requests.get(url).json()['Data'][1]['close']
	else:
		unit_cost_basis = float(row[buyunitcost_row])

	# create and return the buy object
	return Buy(asset, unit_cost_basis, qty, timestamp)	


def csv_sell(row):
	asset = row[sellcoin_row]
	qty = float(row[sellcoinqty_row])
	
	# get the timestamp and print
	timestamp = datetime.strptime(row[date_row], timestamp_format)

	print('Importing ' + timestamp.strftime("%m/%d/%Y %H:%M:%S") + ' Importing Sell From CSV')

	if 'Sold Unit Value' in row:
		unit_cost_basis = row['Sold Unit Value']
	else:
		url = f'{historical_price_base_url}{tsym}&{fsym}{asset}&{limit}{to_ts}{timestamp.timestamp()}&{api_key}'

		unit_cost_basis = requests.get(url).json()['Data'][1]['close']

	new_sell = Sell(asset, unit_cost_basis, qty, timestamp)

	return new_sell


def csv_trade(row):

	sell_asset = row[sellcoin_row]
	sell_qty = float(row[sellcoinqty_row])
	sell_cost_basis = row[sellunitcost_row]

	timestamp = datetime.strptime(row[date_row], timestamp_format)

	print('Importing ' + timestamp.strftime("%m/%d/%Y %H:%M:%S") + ' Trade From CSV')
	
	if 'Sold Unit Value' in row:
		sell_unit_cost_basis = row['Sold Unit Value']
	else:
		url = f'{historical_price_base_url}{tsym}&{fsym}{sell_asset}&{limit}{to_ts}{timestamp.timestamp()}&{api_key}'

		sell_unit_cost_basis = requests.get(url).json()['Data'][1]['close']

	new_sell = Sell(sell_asset, sell_unit_cost_basis, sell_qty, timestamp)

	buy_asset = row[buycoin_row]

	add_asset(buy_asset)

	buy_qty = float(row[buycoinqty_row])

	if row[buyunitcost_row] == '':
		url = f'{historical_price_base_url}{tsym}&{fsym}{buy_asset}&{limit}{to_ts}{asset_date.timestamp()}&{api_key}'

		buy_unit_cost_basis = requests.get(url).json()['Data'][1]['close']
	else:
		buy_unit_cost_basis = float(row[buyunitcost_row])

	new_buy = Buy(buy_asset, buy_unit_cost_basis, buy_qty, timestamp)

	new_buy.part_of_trade(new_sell)
	new_sell.part_of_trade(new_buy)

	return [new_buy, new_sell]


def process_tax(buys):

	# iterate through the buys
	for buy in buys:

		print('')
		print('********************************************************************************************************')
		print(f'{buy.timestamp.strftime("%m/%d/%Y %H:%M:%S")} BUY: {round(buy.og_amount,5)} {buy.asset} @ {"${:,.2f}".format(buy.cost_basis)}/{buy.asset} - {"${:,.2f}".format(buy.cost_basis*buy.og_amount)} total - {round(buy.amount, 5)} remaining')
		print('********************************************************************************************************')

		i = 1

		# iterate through the sell events
		for event in buy.get_sell_events():

			gain = event['profit_loss']

			buy.gains.append(gains)

			if event['days_held'] >= longterm_days:
				# long term capital gain rate
				tax = round(gain * longterm_2020, 2)

			else:
				# short term capital gain rate
				tax = round(gain * shortterm_2020, 2)

			buy.tax_events.append({'gainloss': gain, 'date_bought': buy.timestamp, 'date_sold': event['timestamp'], 'tax': tax})

			if event['trade']:
				print(f"{i} - TRADE: {event['timestamp'].strftime('%m/%d/%Y %H:%M:%S')}: {round(event['qty'],5)} {event['asset']} at {'${:,.2f}'.format(event['unit_cost_basis'])}/{event['asset']} with a profit/loss of {'${:,.2f}'.format(gain)} and a taxable value of {'${:,.2f}'.format(tax)}")
			else:
				print(f"{i} - SELL : {event['timestamp'].strftime('%m/%d/%Y %H:%M:%S')}: {round(event['qty'],5)} {event['asset']} at {'${:,.2f}'.format(event['unit_cost_basis'])}/{event['asset']} with a profit/loss of {'${:,.2f}'.format(gain)} and a taxable value of {'${:,.2f}'.format(tax)}")
			
			taxes[str(event['timestamp'].year)].append(tax)
			gains[str(event['timestamp'].year)].append(gain)

			i = i + 1
        

# simply reads the history and returns it in an array of transactions
def read_csv(file_name):

	with open(file_name, mode='r') as historyinput:
		reader = csv.DictReader(historyinput)

		rows = []

		for row in reader:
			rows.append(row)

	return rows

def process(trans, buys=buys, sells=sells):

	# initalize rows array
	rows = []

	# iterate through all transactions
	for row in trans:

		# if transaction is one that you recieve crypto from
		if row[type_row] == 'Buy' or row[type_row] == 'Recieve' or row[type_row] == 'Air':
			
			# copy row for appending data too
			write_row = row

			# process the buy
			new_buy = csv_buy(row)

			# add buy to the buys container object
			buys.append(new_buy)

			# create the sold value and sold unit value
			write_row['Sold Value'] = ''
			write_row['Sold Unit Value'] = ''

			# add the written data to the new array
			rows.append(write_row)

		# if transaction is one where you lose crypto
		if row[type_row] == 'Send':

			# copy row for appending data too
			write_row = row

			# process the sell
			new_sell = csv_sell(row)

			# create the sold value and sold unit value
			write_row['Sold Value'] = new_sell.unit_cost_basis * new_sell.og_amount
			write_row['Sold Unit Value'] = new_sell.unit_cost_basis

			#add the sell to the sells container object
			sells.append(new_sell)

			# add the written data to the new array
			rows.append(write_row)

		# if transaction is a crypto to crypto event
		if row[type_row] == 'Trade':

			# copy row for appending data too
			write_row = row

			# process the trade
			new_trade = csv_trade(row)

			# create the sold value and sold unit value
			write_row['Sold Value'] = new_trade[1].unit_cost_basis * new_trade[1].og_amount
			write_row['Sold Unit Value'] = new_trade[1].unit_cost_basis

			# append the buy and sell to their container objects
			buys.append(new_trade[0])
			sells.append(new_trade[1])

			# add the written data to the new array
			rows.append(write_row)

	# need to write to rows here with the new unit costs
	try:
	    with open('output_results.csv', 'w') as csvfile:
	        writer = csv.DictWriter(csvfile, fieldnames=headers)
	        writer.writeheader()
	        for data in rows:
	            writer.writerow(data)
	    print('Data Wrote')
	except IOError:
	    print("I/O error")
	# process the data
	return_data = process_history()

	# overwrite the buys and sells container objects with the processed versions
	buys = return_data[0]
	sells = return_data[1]

	# process the tax
	process_tax(buys)

	return (buys, sells)


# iterates through the sells and ties them to the first available buy to calculate a FIFO cast basis for all events
def process_history(buys=buys, sells=sells):

	# sort the buys and sells by timestamp to ensure FIFO operation
	buys = sorted(buys, key=lambda item: item.timestamp)
	sells = sorted(sells, key=lambda item: item.timestamp)

	# iterate through the sells to process them
	for asset_sell in sells:

		# iterate through the buys to find the first available to apply the sell on
		for asset_buy in buys:

			# buy has not been depleated by sells yet and is the same coin/token
			if not asset_buy.is_sold() and asset_buy.asset == asset_sell.asset:

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

def get_coins_held():
	return coins_held

def main():
	read_csv()


if __name__ == "__main__":
    main()


	