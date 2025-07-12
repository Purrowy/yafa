from flask import Flask, render_template
from routes.acc_manager import acc_manager
from routes.transactions import transactions
from routes.find_transactions import find_transactions
from db_helpers import fetch_data_index, create_db

app = Flask(__name__)
app.register_blueprint(acc_manager)
app.register_blueprint(transactions)
app.register_blueprint(find_transactions)


@app.route("/")
def main():
    categories = ['Food', 'Bills', 'Fun']
    recent, accounts, total = fetch_data_index()
    # total[0][0] ponieważ fetch_data_index zwraca listę tupli
    return render_template('index.html', recent = recent, accounts = accounts, total = total[0][0], categories = categories)

if __name__ == "__main__":
    create_db()
    app.run(debug=True)