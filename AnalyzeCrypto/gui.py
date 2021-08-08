import PySimpleGUI as sg

sg.theme('DarkAmber')   # Add a touch of color

def make_main_window():

    layout = [[sg.Text('Process History'), sg.B('Start', key='-PROCESSHISTORY-')],
             [sg.Button('Close')]]

    return sg.Window('Analyze Crypto', layout, finalize=True)

 # Create the Window
main_window = make_main_window()

# Event Loop to process "events" and get the "values" of the inputs
while True:
    window, event, values = sg.read_all_windows()
    print(window, event, values)

    if window == main_window:
    	pass

    if window == main_window and event in (sg.WIN_CLOSED, 'Close'):
        break

    print('Loop End')


main_window.close()