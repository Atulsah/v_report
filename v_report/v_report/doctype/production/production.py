# Copyright (c) 2022, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import os.path
from google.oauth2.service_account import Credentials
from google.oauth2 import service_account
import gspread

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

credentials = {
    "type": "service_account",
    "project_id": "erpnext-victory",
    ".......
}

gc = gspread.service_account_from_dict(credentials)
sh = gc.open("DI ITEM SHEET")

wks = sh.worksheet("2022-APR")
items = wks.get_all_records()
for i in items:
	print(i['buyer'], i['item_code'], i['item_name'], i['in_01'])


class Production(Document):

    def get_gspread_data():
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]

        credentials = {
            "type": "service_account",
            "project_id": "erpnext-victory",
            ......
        }

        gc = gspread.service_account_from_dict(credentials)
        sh = gc.open("DI ITEM SHEET")

        wks = sh.worksheet("2022-APR")
        items = wks.get_all_records()

    def create_stock_entry(doc, handler=""):
        se = frappe.new_doc("Stock Entry")
        se.update({ "series" : MAT/.{buyer}.-.{posting_date}./.###, "purpose": "Manufacture" , "stock_entry_type": "Manufacture" , "to_warehouse": "SIP- Finish Goods - VIWL" })
        for se_item in doc.items:
            se.append("items", { "item_code":se_item.item_code, "item_group": se_item.item_group, "item_name":se_item.item_name, "amount":se_item.amount, "qty": se_item.qty , "uom":se_item.uom, "conversion_factor": se_item.conversion_factor }) 
        frappe.msgprint('Stock Entry is created please submit the stock entry')
        se.insert()
pass
