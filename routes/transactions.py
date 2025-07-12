from flask import Blueprint, render_template, request, redirect
from datetime import datetime
import sqlite3
from db_helpers import insert_transaction, fetch_from_db, delete_table_row, fetch_tr_details, update_transaction

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

    # wylicz nowy total
    temp = fetch_from_db("select amount from Accounts WHERE bank = ?", (bank,))
    current_acc_total = temp[0]['amount']
    new_acc_total = current_acc_total - float(amount)
    print(new_acc_total)
    
    # wsadź je do db transactions
    insert_transaction(date, category, desc, bank, amount)

    # update nowy total
    with sqlite3.Connection(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE Accounts SET amount = ? WHERE bank = ?", (new_acc_total, bank,))
        conn.commit()

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

        # dodać walidację

        update_transaction(dict(data))

        return redirect(request.referrer)