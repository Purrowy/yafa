from flask import Blueprint, render_template, request, redirect
from db_helpers import fetch_from_db

raport = Blueprint('raport', __name__, template_folder='templates')

@raport.route('/raport', methods=['GET'])
def show_raport():
    data = fetch_from_db('select Transactions.*, Accounts.bank as account FROM Transactions JOIN Accounts ON Transactions.account_id = Accounts.id')
    return render_template('raport.html', data=data)