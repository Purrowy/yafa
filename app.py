from flask import Flask, render_template
from routes.acc_manager import acc_manager
from routes.transactions import transactions
from routes.report import report
from db_helpers import create_db
from scrap import get_dashboard_data

app = Flask(__name__)
app.register_blueprint(acc_manager)
app.register_blueprint(transactions)
app.register_blueprint(report)


@app.route("/")
def main():
    accounts, total, recent, categories = get_dashboard_data()
    return render_template('index.html', recent = recent, accounts = accounts, total = total, categories = categories)

if __name__ == "__main__":
    create_db()
    app.run(debug=True)