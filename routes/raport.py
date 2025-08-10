from flask import Blueprint, render_template, request, redirect
from db_helpers import fetch_from_db, Transactions

raport = Blueprint('raport', __name__, template_folder='templates')
tx = Transactions()

@raport.route('/raport', methods=['GET'])
def show_raport():
    #data = fetch_from_db('select Transactions.*, Accounts.bank as account FROM Transactions JOIN Accounts ON Transactions.account_id = Accounts.id')
    data = tx.sum_transactions_by_categories("2025-08%")
    print(data)
    return render_template('raport.html', data=data)