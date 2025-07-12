from flask import Blueprint, render_template, request
import sqlite3
from db_helpers import fetch_from_db, list_accounts

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
            cursor.execute("select * from Transactions")
        else:
            cursor.execute("select * from Transactions WHERE account = ?", (temp,))
        records = cursor.fetchall()
    
    rows = fetch_from_db("select * from Transactions")

    return render_template("table.html", accounts=accounts, rows=rows, records=records) 