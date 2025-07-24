from flask import Blueprint, render_template, request, redirect
from datetime import datetime
import sqlite3
from db_helpers import insert_transaction, list_accounts, delete_table_row, fetch_tr_details, update_transaction, get_account_id

DATABASE = "test.db"

transactions = Blueprint('transactions', __name__)


# pobierz dane z formularza na stronie głównej, wsadź je do tabeli Transactions i zupdateuj
# amounts o nowy total
@transactions.route("/submit_transaction", methods=["POST"])
def submit_transaction():
    
    # pobierz dane wysłane od użytkownika
    date = request.form.get("timestamp")
    if date == "":
        date = datetime.now().strftime("%Y-%m-%d %H:%M")
    category = request.form.get("category")
    desc = request.form.get("desc")
    bank = request.form.get("bank")
    amount = request.form.get("amount")

    # znajdz acc_id
    account_id = get_account_id(bank)
    
    # wsadź je do db transactions
    insert_transaction(date, category, desc, account_id, amount)

    return redirect("/")

@transactions.route("/delete_transaction", methods=["POST"])
def delete_transaction():
    id = request.form.get("id")
    table = "Transactions"
    delete_table_row(table, id)
    # https://stackoverflow.com/questions/41270855/flask-redirect-to-same-page-after-form-submission
    return redirect(request.referrer)

@transactions.route("/transaction_details", methods=["POST", "GET"])
def transaction_details():
    
    if request.method == 'GET':
        # https://www.tutorialspoint.com/how-to-process-incoming-request-data-in-flask
        id = request.args.get('id')
        if id.isdigit():
            tr_data = fetch_tr_details(id)
            return render_template("tr_details.html", tr_data=tr_data, id=id)
        else:
            return ("Invalid ID")    
    
    if request.method == 'POST':
        data = request.form

        # check against current list of accs
        accounts = list_accounts()
        valid_bank = False
        for acc in accounts:
            if data.get("account") == acc["bank"]:
                print("essa")
                valid_bank = True

        # https://stackoverflow.com/questions/354038/how-do-i-check-if-a-string-represents-a-number-float-or-int
        amount = data.get("amount")
        try:
            float(amount)
        except ValueError:
            return redirect(request.referrer)

        if not valid_bank or not amount:
            print("issues")
            return redirect(request.referrer)

        update_transaction(dict(data))

        return redirect(request.referrer)