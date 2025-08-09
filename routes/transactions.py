from flask import Blueprint, render_template, request, redirect
from datetime import datetime
from scrap import validate_bank_account
from db_helpers import get_account_id, Transactions, list_accounts, Categories

transactions = Blueprint('transactions', __name__)

tx = Transactions()
cs = Categories()

# pobierz dane z formularza na stronie głównej, wsadź je do tabeli Transactions
@transactions.route("/submit_transaction", methods=["POST"])
def submit_transaction():
    
    # pobierz dane wysłane od użytkownika
    date = request.form.get("timestamp")
    if date == "":
        date = datetime.now().strftime("%Y-%m-%d")
    category = request.form.get("category")
    category_id = cs.get_category_id(category)
    desc = request.form.get("desc")
    # html przekazuje bank i name razem, need to split
    bank, name = request.form.get("bank").split("|")
    amount = request.form.get("amount")

    if not validate_bank_account(bank, name):
        return redirect("/")

    # znajdz acc_id
    account_id = get_account_id(bank, name)
    
    # wsadź je do db transactions
    tx.insert_new_transaction(date, account_id, category_id, amount, description=desc)

    return redirect("/")

@transactions.route("/delete_transaction", methods=["POST"])
def delete_transaction():
    tr_id = request.form.get("id")
    tx.delete_transaction(tr_id)
    # https://stackoverflow.com/questions/41270855/flask-redirect-to-same-page-after-form-submission
    return redirect(request.referrer)

@transactions.route("/transaction_details", methods=["POST", "GET"])
def transaction_details():

    # przy GET pobierz full dane transakcji i wyświetl
    if request.method == 'GET':
        # https://www.tutorialspoint.com/how-to-process-incoming-request-data-in-flask
        tr_id = request.args.get('id')
        if tr_id.isdigit():
            data = tx.get_transaction(tr_id, "full")
            tr_data = [dict(data)]
            return render_template("tr_details.html", tr_data=tr_data, id=tr_id)
        else:
            return ("Invalid ID")    

    # przy POST zupdateuj transakcje o nowe info
    elif request.method == 'POST':
        data = request.form
        account_id = get_account_id(data["bank"], data["name"])
        category_id = cs.get_category_id(data["category"])

        # https://stackoverflow.com/questions/354038/how-do-i-check-if-a-string-represents-a-number-float-or-int
        amount = data["amount"]
        try:
            float(amount)
        except ValueError:
            return redirect(request.referrer)

        if not account_id or not amount:
            print("issues")
            return redirect(request.referrer)

        tx.update_transaction(data["id"], timestamp=data["timestamp"], description=data["description"], category_id=category_id, amount=amount, account_id=account_id, debit=data["debit"])

        return redirect(request.referrer)

@transactions.route("/find_transactions", methods=["GET"])
def find_transactions():

    try:
        if not request.args.get("account"):
            account_id = '%'
        else:
            bank, name = request.args.get("account").split("|")
            account_id = get_account_id(bank, name)
    except ValueError:
        return redirect("/find_transactions")

    accounts = list_accounts()
    # dane do overview table
    records = tx.get_all_transactions(account_id)

    return render_template("find_transactions.html", accounts=accounts, records=records)