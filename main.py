import requests
import pandas as pd
import PySimpleGUI as sg

dtypes = {
    "settlement-id": "category",
    "settlement-start-date": "category",
    "settlement-end-date": "category",
    "deposit-date": "category",
    "total-amount": "float64",
    "currency": "category",
    "transaction-type": "category",
    "order-id": "category",
    "merchant-order-id": "category",
    "adjustment-id": "category",
    "shipment-id": "category",
    "marketplace-name": "category",
    "amount-type": "category",
    "amount-description": "category",
    "amount": "float64",
    "fulfillment-id": "category",
    "posted-date": "category",
    "posted-date-time": "category",
    "order-item-code": "category",
    "merchant-order-item-id": "category",
    "merchant-adjustment-item-id": "category",
    "sku": "category",
    "quantity-purchased": "Int64",
    "promotion-id": "category",
}

API_KEY = '' #API key for exchangerate-api.com / depreceated

def get_flatfile_input():
    '''Asks for an Amazon Celler Central flat file payment report (v2) via GUI interface. Returns a list consting of the file and the filename'''
    flatfile_form = sg.FlexForm('Settlement Currency Exchange') 
    layout = [
          [sg.Text('Please select Flat File (v2)')],
          [sg.Text('Statement File: ', size=(50, 1)), sg.FileBrowse()],
          [sg.Submit(), sg.Cancel()]
         ]
    button, filename = flatfile_form.Layout(layout).Read() 
    flat_file = filename['Browse']
    file_name = flat_file.rsplit('/', 1)[-1][:-4] #this gets only the file name without the full path / file extension
    flatfile_form.close()
    settlement_df = pd.read_table(flat_file, sep='\t', dtype=dtypes)
    return [settlement_df, file_name]

def ask_for_currency_type():
    '''Asks for currency type to exchange from (CAD or MXN) via GUI menu radio buttons'''
    currency_form = sg.FlexForm('Settlement Currency Exchange') 
    layout = [
            [sg.Text('What currency are you converting from?')],
            [sg.Radio("Canadian Dollars (CAD)", "Radio1", default=False)], 
            [sg.Radio("Mexican Peso (MXN)", "Radio2", default=False)],
            [sg.Submit(), sg.Cancel()]
            ]
    button, currency_selection =  currency_form.Layout(layout).Read() 
    currency_form.close()
    if currency_selection[0] == currency_selection[1]:
        print(currency_selection[0])
        print(currency_selection[1])
        sg.popup_error("Error, invalid selection. Please select only one currency. Try again.")
        raise Exception("Error, both currencies selected.")
    elif currency_selection[0]:
        return "CAD"
    elif currency_selection[1]:
        return "MXN"
    else:
        sg.popup_error("Unknown error")
        raise Exception("Unknown error!")

def ask_for_deposit_total():
    '''Asks for the deposited amount in USD''' 
    layout = [[sg.Text('Deposit Amount (USD):')],
            [sg.InputText()],
            [sg.Button('Submit')]]
    window = sg.Window('Settlement Currency Exchange', layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == 'Submit':
            #print(f'You entered: {values[0]}')
            break
    window.close()
    return values[0]


def ask_for_previous_rate():
    '''Asks for the previous deposit rate''' 
    layout = [[sg.Text('Previous Conversion Rate')],
            [sg.InputText()],
            [sg.Button('Submit')]]
    window = sg.Window('Settlement Currency Exchange', layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == 'Submit':
            #print(f'You entered: {values[0]}')
            break
    window.close()
    return values[0]

'''def get_exchange_rate(currency_type):
    Gets the current exchange rate from exchangerate-api.com
    #no longer using this
    if currency_type == "CAD":
        url = "https://v6.exchangerate-api.com/v6/" + API_KEY + "/latest/CAD"
        response = requests.get(url)
        data = response.json()
        conversion_rate = data["conversion_rates"]["USD"]
        return conversion_rate
    elif currency_type == "MXN":
        url = "https://v6.exchangerate-api.com/v6/" + API_KEY + "/latest/MXN"
        response = requests.get(url)
        data = response.json()
        conversion_rate = data["conversion_rates"]["USD"]
        return conversion_rate
    else:
        raise Exception("Error, unable to convert currency")'''



def get_exchange_rate(deposit_amount, settlement_df):
    '''Gets the exchange rate used based on a USD deposit total.'''
    #TODO dont count previous reserve
    foreign_total = settlement_df['total-amount'].sum()
    current_rate = deposit_amount / foreign_total
    layout = [[sg.Text('Current Conversion Rate: ' + str(current_rate))],
            [sg.Button('Ok')]]
    window = sg.Window('Settlement Currency Exchange', layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == 'Ok':
            break
    window.close()
    return current_rate

def convert_currency(settlement_dataframe: pd.DataFrame, exchange_rate, previous_rate) -> pd.DataFrame:
    '''Accepts the settlement flatfile dataframe and exchange rate as arguments'''
    previous_reserve = settlement_dataframe['amount'].loc[(settlement_dataframe['amount-description']== 'Previous Reserve Amount Balance')].sum()
    print('Previous Reserve = ' + str(previous_reserve))
    settlement_dataframe['amount'] = settlement_dataframe['amount'] * exchange_rate 
    settlement_dataframe['amount'].loc[(settlement_dataframe['amount-description'] == 'Previous Reserve Amount Balance')] = (settlement_dataframe['amount'].loc[(settlement_dataframe['amount-description'] == 'Previous Reserve Amount Balance')] / exchange_rate) * previous_rate
    return settlement_dataframe

def output_to_txt(converted_df: pd.DataFrame, filename):
    '''Outputs the dataframe to tab delimited text file using the prefix + filename'''
    converted_df.to_csv("Converted_" + filename + ".txt", sep = '\t', index=False)
    sg.popup('File saved as Converted_' + filename + '.txt')

def main():
    settlement_df = get_flatfile_input()
    file_name = settlement_df[1] #gets the file name
    settlement_df = settlement_df[0] #overwrites the variable now that we have the filename
    #currency_type = ask_for_currency_type()
    deposit_total = float(ask_for_deposit_total())
    previous_rate = float(ask_for_previous_rate())
    #exchange_rate = get_exchange_rate(currency_type)
    exchange_rate = get_exchange_rate(deposit_total, settlement_df)
    #TODO Print exchange rate
    converted_df = convert_currency(settlement_df, exchange_rate, previous_rate)
    output_to_txt(converted_df, file_name)
    
if __name__ == "__main__":
    main()