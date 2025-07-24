from flask import Blueprint, render_template, request, abort, redirect
from datetime import datetime, date
from db_helpers import create_bank_account, list_accounts, insert_into_snapshot, get_account_id, get_current_balance, update_snapshot
import sqlite3

DATABASE = "test.db"
date = datetime.now().strftime("%Y-%m")

acc_manager = Blueprint('acc_manager', __name__, template_folder='templates')

@acc_manager.route('/accounts', methods=["POST", "GET"])
def manager():
    if request.method == 'GET':

        with sqlite3.Connection(DATABASE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * from Accounts")
            temp = cursor.fetchall()
            accounts_data = [dict(t) for t in temp]

        for acc in accounts_data:
            acc["amount"] = get_current_balance(acc["id"])

        return render_template("acc_manager.html", accounts_data=accounts_data)

    elif request.method == 'POST':
        bank = request.form.get("bank")
        new_amount = request.form.get("amount")

        # check against current list of accs
        accounts = list_accounts()
        valid_bank = False
        for acc in accounts:
            if bank == acc["bank"]:
                valid_bank = True

        if not valid_bank or not new_amount.isnumeric():
            print("fail")
            return redirect("/accounts")
        else:
            try:
                account_id = get_account_id(bank)
                update_snapshot(account_id, date, new_amount)
                print("snapshot")
            except:
                print("not unique")
            return redirect("/accounts")

@acc_manager.route('/add_acc', methods=["POST"])
def add_acc():
    if request.method == 'POST':
        bank = request.form.get("bank")
        name = request.form.get("name")
        amount = request.form.get("amount")
        if not amount.isnumeric():
            return redirect("/accounts")
        create_bank_account(bank, name)
        acc_id = get_account_id(bank)
        insert_into_snapshot(acc_id, date, amount)

        return redirect('/accounts')
    else:
        return "nope", 400