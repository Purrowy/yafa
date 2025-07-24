from flask import Blueprint, render_template, request
import sqlite3
from db_helpers import fetch_from_db, list_accounts, get_account_id

# move to transaction.py

DATABASE = "test.db"

find_transactions = Blueprint('find_transactions', __name__)

@find_transactions.route("/find", methods=["GET"])
def find():
    accounts = list_accounts()
    temp = request.args.get('account')

        
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if temp == "all":
            cursor.execute("select Accounts.bank as account, Transactions.timestamp, Transactions.amount, Transactions.id from Transactions JOIN Accounts ON Transactions.account_id = Accounts.id")
        else:
            acc_id = get_account_id(temp)
            cursor.execute("select Accounts.bank as account, Transactions.timestamp, Transactions.amount, Transactions.id from Transactions JOIN Accounts ON Transactions.account_id = Accounts.id WHERE Transactions.account_id = ?", (acc_id,))
        records = cursor.fetchall()
    
    rows = fetch_from_db("select * from Transactions")

    return render_template("table.html", accounts=accounts, rows=rows, records=records) 