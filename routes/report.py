from flask import Blueprint, render_template, request, redirect
from db_helpers import Transactions

report = Blueprint('report', __name__, template_folder='templates')
tx = Transactions()

@report.route('/report', methods=['GET'])
def show_report():
    data = tx.sum_transactions_by_categories("2025-08%")
    print(data)
    return render_template('report.html', data=data)