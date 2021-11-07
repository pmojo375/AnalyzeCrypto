import PySimpleGUI as sg
import main

data = []
header_list = []

sg.theme('Default')   # Add a touch of color

def make_main_window():

    layout = [[sg.Text('Process History'), sg.B('Start', key='-PROCESSHISTORY-')],
    		 [sg.I('', key='-CSVFILE-'), sg.FileBrowse('Browse', file_types=(("CSV Files","*.csv")))],
    		 [sg.B('Read CSV', key='-READCSV-')],
             [sg.Button('Close')]]

    return sg.Window('Analyze Crypto', layout, finalize=True)

def get_coins_held_data():
	coins_held = main.get_coins_held()
	coins_held_data = main.get_current(coins_held, buys)

	return coins_held_data


def get_coins_held_list(coins_held_data):

	return_data = []

	for asset in coins_held_data:
		return_data.append(asset)

	return return_data

def make_current_window():
	coins_held_data = get_coins_held_data()
	coins_held = coins_held_data['assets']

	row_i = 0
	row = []
	rows = []

	held = []

	total_amount = 0

	for coin in coins_held:

		total_coin_amount = coins_held_data["amount"][coin]*coins_held_data["rates"][coin]

		if (coins_held_data["amount"][coin]*coins_held_data["rates"][coin]) > 1:

			total_amount = total_amount + total_coin_amount

			held.append([sg.T(f'{"{:,.5f}".format(coins_held_data["amount"][coin])} {coin} at {"${:,.2f}".format(coins_held_data["rates"][coin])}/{coin} or {"${:,.2f}".format(coins_held_data["amount"][coin]*coins_held_data["rates"][coin])} total')])

		row.append(sg.B(coin, key=coin, size=(10,1)))

		row_i = row_i + 1

		if row_i == 4:
			row_i = 0
			rows.append(row)
			row = []

	layout = [[sg.T('Select a coin/token to view details')],
			 [sg.T("${:,.2f}".format(total_amount), size=(30,3), auto_size_text=True)],
			 [held],
			 [rows],
			 [sg.Button('Close')]]

	return sg.Window('Coins', layout, finalize=True)

def make_table():
	layout = [[sg.Table(values=data, headings=header_list, max_col_width=25, auto_size_columns=True, justification='right', num_rows=min(len(data), 20))],
			 [sg.Button('Close')]]

	return sg.Window('Data', layout, finalize=True)

def make_results(buys):

	row_i = 0
	row = []
	rows = []

	for i in range(0, len(buys)):
		row.append(sg.B(f'Buy {i}', key=i, size = (5,1)))

		row_i = row_i + 1

		if row_i == 10:
			row_i = 0
			rows.append(row)
			row = []

	layout = [rows,
			 [sg.Button('Close')]]

	return sg.Window('Data', layout, finalize=True)

def make_details_window(buy):

	events = []

	for e in buy.get_sell_events():
		events.append([sg.T(f"{e['timestamp'].strftime('%m/%d/%Y %H:%M:%S')}: {round(e['qty'],5)} {e['asset']} at {'${:,.2f}'.format(e['unit_cost_basis'])}/{e['asset']} with a profit/loss of {e['profit_loss']} and a taxable value of TODO")])

	layout = [[sg.T(f'{buy.timestamp.strftime("%m/%d/%Y %H:%M:%S")}:{buy.asset} - {buy.og_amount}')],
			 [events],
			 [sg.Button('Close')]]

	return sg.Window('Details', layout, finalize=True)

 # Create the Window
main_window = make_main_window()
table_window = None
details_window = None
results_window = None
current_window = None

transactions = None

# Event Loop to process "events" and get the "values" of the inputs
while True:
	window, event, values = sg.read_all_windows()
	print(event, values)

	if event == sg.WIN_CLOSED:
		break
	if event == 'Close':
		window.close()

		if window == details_window:
			details_window = None
		elif window == table_window:
			table_window = None
		elif window == results_window:
			results_window = None
		elif window == current_window:
			current_window = None
		else:
			break

	if event == '-PROCESSHISTORY-':
		break
	if window == 'Data' and event in range(1, len(buys)+1):
		print(event)
	if event == '-READCSV-':
		# get the list of transactions from the CSV file
		transactions = main.read_csv(values['-CSVFILE-'])

		data = []
		new_row = []
		header_list = []

		# iterate through all transactions
		for row in transactions:

			data.append(list(row.values()))
			header_list = list(row.keys())

		buys_sells = main.process(transactions)

		buys = buys_sells[0]
		sells = buys_sells[1]

		#table_window = make_table()
		#results_window = make_results(sells)

		current_window = make_current_window()

	# button pushed on buy display window
	if event in range(0, len(buys)):
		details_window = make_details_window(buys[int(event)])

window.close()