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
    '''Asks for an Amazon Celler Central flat file payment report (v2) via GUI interface'''
    flatfile_form = sg.FlexForm('Settlement Analyzer') 
    layout = [
          [sg.Text('Please select Flat File (v2)')],
          [sg.Text('Statement File: ', size=(50, 1)), sg.FileBrowse()],
          [sg.Submit(), sg.Cancel()]
         ]
    button, filename = flatfile_form.Layout(layout).Read() 
    flat_file = filename['Browse']
    flatfile_form.close()
    settlement_df = pd.read_table(flat_file, sep='\t', dtype=dtypes)
    return settlement_df

def ask_for_currency_type():
    '''Asks for currency type to exchange from (CAD or MXN) via GUI menu radio buttons'''
    currency_form = sg.FlexForm('Settlement Analyzer') 
    layout = [
            [sg.Text('What currency are you converting from?')],
            [sg.Radio("Canadian Dollars (CAD)", "Radio1", default=False)], 
            [sg.Radio("Mexican Peso (MXN)", "Radio2", default=False)],
            [sg.Submit(), sg.Cancel()]
            ]
    button, currency_selection =  currency_form.Layout(layout).Read() 
    currency_form.close()
    if currency_selection[0]:
        return "CAD"
    elif currency_selection[1]:
        return "MXN"
    else:
        return None

def main():
    get_flatfile_input()
    currency_type = ask_for_currency_type()

if __name__ == "__main__":
    main()