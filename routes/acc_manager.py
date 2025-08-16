from flask import Blueprint, render_template, request, abort, redirect
from datetime import datetime
from db_helpers import create_bank_account, update_account_name, delete_bank_account, Accounts, Snapshot

DATABASE = "test.db"
date = datetime.now().strftime("%Y-%m")
snp = Snapshot()
acs = Accounts()

acc_manager = Blueprint('acc_manager', __name__, template_folder='templates')

@acc_manager.route('/accounts', methods=["POST", "GET"])
def manager():
    if request.method == 'GET':

        accounts_data = acs.get_accounts()

        for acc in accounts_data:
            acc["amount"] = acs.get_account_balance(acc["id"])

        return render_template("acc_manager.html", accounts_data=accounts_data)

    elif request.method == 'POST':

        account_id = get_account_id(request.form.get("bank"), request.form.get("current_name"))

        if not account_id:
            print("Account not found")
            return redirect("/accounts")

        # https://www.freecodecamp.org/news/python-switch-statement-switch-case-example/
        action = request.form.get("submit_button")
        match action:
            case "Change acc name":
                update_account_name(account_id, request.form.get("new_name"))
            case "Delete account":
                try:
                    delete_bank_account(account_id)
                except ValueError:
                    print("Bank account not found")
                    return redirect("/accounts")

        return redirect("/accounts")

@acc_manager.route('/add_acc', methods=["POST"])
def add_acc():
    if request.method == 'POST':
        bank = request.form.get("bank")
        name = request.form.get("name")

        # function used this way to prevent duplicates
        if acs.get_account_id(bank, name):
            print("acc already exists")
            return redirect("/accounts")

        amount = request.form.get("amount")
        if not amount.isnumeric():
            return redirect("/accounts")
        create_bank_account(bank, name)
        acc_id = acs.get_account_id(bank, name)

        return redirect('/accounts')
    else:
        return "nope", 400

@acc_manager.route('/create_snapshot', methods=["POST"])
def create_snapshot():
    snp.create_snapshot()
    return redirect("/accounts")