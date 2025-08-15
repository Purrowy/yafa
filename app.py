from flask import Flask, render_template
from routes.acc_manager import acc_manager
from routes.transactions import transactions
from routes.raport import raport
from db_helpers import fetch_data_index, create_db, Categories
from scrap import get_dashboard_data

app = Flask(__name__)
app.register_blueprint(acc_manager)
app.register_blueprint(transactions)
app.register_blueprint(raport)


@app.route("/")
def main():
    #n = create_acc_snapshots()
    #print(n)
    cs = Categories()
    categories = cs.list_categories()
    accounts, total, recent_transactions = get_dashboard_data()
    return render_template('index.html', recent = recent_transactions, accounts = accounts, total = total, categories = categories)

if __name__ == "__main__":
    create_db()
    app.run(debug=True)