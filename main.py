import requests
import pandas as pd
import PySimpleGUI as sg

dtypes = {
    "settlement-id": "category",
    "settlement-start-date": "category",
    "settlement-end-date": "category",
    "deposit-date": "category",
    "total-amount": "category",
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

API_KEY = 'dccb484c0029bcd76c5b3a87' #API key for exchangerate-api.com

def get_flatfile_input():
    '''Asks for an Amazon Celler Central flat file payment report (v2) via GUI interface. Returns a list c'''
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
        raise Exception("Error, invalid selection")
    elif currency_selection[0]:
        return "CAD"
    elif currency_selection[1]:
        return "MXN"
    else:
        raise Exception("Unknown error!")

def get_exchange_rate(currency_type):
    '''Gets the current exchange rate from exchangerate-api.com'''
    if currency_type == "CAD":
        url = "https://v6.exchangerate-api.com/v6/dccb484c0029bcd76c5b3a87/latest/CAD"
        response = requests.get(url)
        data = response.json()
        conversion_rate = data["conversion_rates"]["USD"]
        return conversion_rate
    elif currency_type == "MXN":
        url = "https://v6.exchangerate-api.com/v6/dccb484c0029bcd76c5b3a87/latest/MXN"
        response = requests.get(url)
        data = response.json()
        conversion_rate = data["conversion_rates"]["USD"]
        return conversion_rate
    else:
        raise Exception("Error, unable to convert currency")

def convert_currency(settlement_dataframe: pd.DataFrame, exchange_rate) -> pd.DataFrame:
    '''Accepts the settlement flatfile dataframe and exchange rate as arguments'''
    settlement_dataframe['amount'] = settlement_dataframe['amount'] * exchange_rate
    return settlement_dataframe

def output_to_csv(converted_df: pd.DataFrame, filename):
    '''Outputs the dataframe to csv using the prefix + filename'''
    converted_df.to_csv("Converted_" + filename + ".csv")
    layout = [[sg.Text('File saved as "Converted_' + filename + ".csv")],
          [sg.Button('Thanks!')]]
    window = sg.Window('Success!', layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Thanks!':
            break

def main():
    settlement_df = get_flatfile_input()
    file_name = settlement_df[1] #gets the file name
    settlement_df = settlement_df[0] #overwrites the variable now that we have the filename
    currency_type = ask_for_currency_type()
    exchange_rate = get_exchange_rate(currency_type)
    converted_df = convert_currency(settlement_df, exchange_rate)
    output_to_csv(converted_df, file_name)
    
if __name__ == "__main__":
    main()