from flask import Blueprint, render_template, request, abort, redirect
from db_helpers import update_table_row, add_new_account, list_accounts, sum_from_table
import sqlite3

DATABASE = "test.db"

acc_manager = Blueprint('acc_manager', __name__, template_folder='templates')

@acc_manager.route('/accounts', methods=["POST", "GET"])
def manager():
    if request.method == 'GET':

        with sqlite3.Connection(DATABASE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * from Accounts")
            accounts_data = cursor.fetchall()
        
        return render_template("acc_manager.html", accounts_data=accounts_data)
    
    elif request.method == 'POST':
        id = request.form.get("id")
        new_amount = request.form.get("amount")
        print(id, new_amount)
        update_table_row("Accounts", "amount", new_amount, id)

        return redirect("/accounts")
    
@acc_manager.route('/add_acc', methods=["POST"])
def add_acc():
    if request.method == 'POST':
        bank = request.form.get("bank")
        name = request.form.get("name")
        amount = request.form.get("amount")
        add_new_account(bank, name, amount)
        return redirect('/accounts')
    else:
        return "nope", 400

# wip, logic is off, invoke button removed from html
@acc_manager.route('/sync', methods=["POST"])
def sync_acc_totals():

    # get list of unique accounts
    accounts = list_accounts()

    # query each account in Transaction and update Account table with new value
    for account in accounts:
        new_amount = sum_from_table("Transactions", account['bank'])
        print(account['bank'])
        print (new_amount[0][0])
        update_table_row("Accounts", "amount", new_amount[0][0], account['id'])

    return redirect("/accounts")