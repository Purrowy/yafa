import sqlite3
from pathlib import Path
from datetime import datetime
import dateutil.relativedelta

DATABASE = "test.db"
currentMonth = datetime.now().strftime("%Y-%m")

class Snapshot:
    def __init__(self, db_path=DATABASE):
        self.db_path = db_path

    def create_snapshot(self):
        print("create_snapshot called db")
        pass

class Accounts:
    def __init__(self, db_path=DATABASE):
        self.db_path = db_path

    def get_accounts(self, mode="all"):

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        match mode:
            case "all":
                query = '''SELECT id, bank, name FROM Accounts'''
                cursor.execute(query)
            case _:
                query = '''SELECT id, bank, name FROM Accounts WHERE id = ?'''
                cursor.execute(query, (mode,))

        accounts_data = cursor.fetchall()
        result = [dict(a) for a in accounts_data]
        return result

class Categories:
    def __init__(self, db_path=DATABASE):
        self.db_path = db_path

    def create_table(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # category_type: I = incoming, F = fixed, V = variable, P = planned/future

            query = '''
                    CREATE TABLE IF NOT EXISTS Categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_name TEXT NOT NULL,
                    category_type TEXT NOT NULL,
                    UNIQUE (category_name, category_type)
                    )
                    '''
            cursor.execute(query)
            conn.commit()

    def create_new_category(self, category_name, category_type):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = '''INSERT INTO Categories (category_name, category_type) VALUES (?, ?)'''
            cursor.execute(query, (category_name, category_type))
            conn.commit()

    def list_categories(self, category_type="_"):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            query = '''SELECT category_name as name from Categories
                        WHERE category_type LIKE ?
                        ORDER BY category_name'''
            cursor.execute(query, (category_type,))
            rows = cursor.fetchall()
            categories = [dict(r) for r in rows]
            return categories

    def get_category_id(self, category_name):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = '''SELECT id from Categories WHERE category_name = ?'''
            cursor.execute(query, (category_name,))
            category_id = cursor.fetchone()[0]
            return category_id

class Transactions:

    def __init__(self, db_path=DATABASE):
        self.db_path = db_path

    # https://stackoverflow.com/questions/9539921/how-do-i-define-a-function-with-optional-arguments
    # https://stackoverflow.com/questions/67890858/how-to-insert-variable-number-of-values-into-a-table-in-sqlite-using-prepared-st
    # https://stackoverflow.com/questions/34092528/pythonic-way-to-check-if-a-variable-was-passed-as-kwargs

    def insert_new_transaction(self, timestamp, account_id, category_id, amount, **kwargs):

        # ustaw jako None/1 jesli nie zostało podane jako param
        description = kwargs.get("description", None)
        debit = kwargs.get("debit", 1)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = "INSERT INTO transactions (account_id, amount, timestamp, description, category_id, debit) VALUES (?, ?, ?, ?, ?, ?)"
            cursor.execute(query, (account_id, amount, timestamp, description, category_id, debit))
            conn.commit()

    def get_transaction(self, transaction_id, mode="default"):
        with sqlite3.connect(self.db_path) as conn:
            # bez sqlite3.Row nie działa transaction.keys()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            match mode:
                case "default":
                    query = "SELECT * FROM Transactions WHERE id = ?"
                case "full":
                    query = '''
                            SELECT Transactions.id, Transactions.timestamp,
                                Accounts.bank as bank, Accounts.name as name,
                                Categories.category_name as category, Transactions.description,
                                Transactions.debit, Transactions.amount
                            FROM Transactions
                                JOIN Accounts ON Transactions.account_id = Accounts.id
                                JOIN Categories ON Transactions.category_id = Categories.id
                            WHERE Transactions.id = ?
                            '''

            cursor.execute(query, (transaction_id,))
            transaction = cursor.fetchone()
            return transaction

    def get_all_transactions(self, account_id):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = '''
                    select Accounts.bank as bank, Accounts.name as name, 
                    Transactions.timestamp, Transactions.amount, 
                    Transactions.id from Transactions JOIN Accounts ON Transactions.account_id = Accounts.id 
                    WHERE Transactions.account_id LIKE ?
                    '''

            cursor.execute(query, (account_id,))
            transactions = cursor.fetchall()
            return transactions

    def update_transaction(self, transaction_id, **kwargs):

        original_tr_data = self.get_transaction(transaction_id)

        timestamp = kwargs.get("timestamp", original_tr_data["timestamp"])
        description = kwargs.get("description", original_tr_data["description"])
        category_id = kwargs.get("category_id", original_tr_data["category_id"])
        debit = kwargs.get("debit", original_tr_data["debit"])
        account_id = kwargs.get("account_id", original_tr_data["account_id"])
        amount = kwargs.get("amount", original_tr_data["amount"])

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = '''UPDATE transactions
                       SET account_id = ?,
                           amount = ?,
                           timestamp = ?,
                           description = ?,
                           category_id = ?,
                           debit = ?
                       WHERE id = ?'''
            cursor.execute(query, (account_id, amount, timestamp, description, category_id, debit, transaction_id))
            conn.commit()

    def delete_transaction(self, transaction_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = "DELETE FROM transactions WHERE id = ?"
            cursor.execute(query, (transaction_id,))
            conn.commit()

    def sum_transactions_by_categories(self,time_range):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            query = '''SELECT Categories.category_name as category, Categories.category_type as type, SUM(Transactions.amount) as total from Transactions 
                       JOIN Categories ON Transactions.category_id = Categories.id
                       WHERE Transactions.timestamp LIKE ?
                       GROUP BY Transactions.category_id'''
            # WHERE Transactions.timestamp LIKE '2025-08%'
            cursor.execute(query, (time_range,))
            rows = cursor.fetchall()
            result = [dict(r) for r in rows]
            return result

# params żeby nie wrzucać query jako formatted stringa
def fetch_from_db(query, params=()):
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return rows

def fetch_data_index():
    accounts = list_accounts()
    recent = fetch_from_db("select Transactions.*, Accounts.bank as account FROM Transactions JOIN Accounts ON Transactions.account_id = Accounts.id ORDER BY id DESC LIMIT 5")
    total = 0
    for acc in accounts:
        acc['amount'] = get_current_balance(acc['id'], currentMonth)
        total = total + acc["amount"]

    return recent, accounts, total

def get_current_balance(account, snapshot_date):
    if not snapshot_date:
        snapshot_date = currentMonth
    try:
        current_balance = fetch_from_db(f"select amount from snapshots WHERE account_id = {account} AND snapshot_date = '{snapshot_date}'")[0][0]
        amount_spent = fetch_from_db(f"SELECT SUM(amount) FROM Transactions where account_id = {account} AND timestamp LIKE '{snapshot_date}%'")[0][0]
    except:
        current_balance = 0
        amount_spent = 0
    try:
        current_balance = float(current_balance) - float(amount_spent)
    except:
        pass
    return current_balance

def get_snapshot_amount(account_id, date):
    con = sqlite3.connect(DATABASE)
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    query = "SELECT amount FROM snapshots WHERE account_id = ? AND snapshot_date = ?"
    cursor.execute(query, (account_id, date, ))
    result = cursor.fetchone()[0]
    return result

def list_accounts():
    # https://stackoverflow.com/questions/3300464/how-can-i-get-dict-from-sqlite-query
    con = sqlite3.connect(DATABASE)
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    cursor.execute("SELECT id, bank, name from Accounts")
    temp = cursor.fetchall()
    result = [dict(t) for t in temp]
    return result

def get_account_id(bank, name):
    try:
        #https://stackoverflow.com/questions/30294515/converting-sqlite3-cursor-to-int-python
        con = sqlite3.connect(DATABASE)
        con.row_factory = sqlite3.Row
        cursor = con.cursor()
        query = "SELECT id FROM Accounts WHERE bank = ? AND name = ?"
        cursor.execute(query, (bank, name, ))
        account_id = cursor.fetchone()[0]
        return account_id
    except:
        return False

def update_account_name(account_id, new_name):
    query = "UPDATE Accounts SET name = ? WHERE id = ?;"
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (new_name, account_id, ))
        conn.commit()

def create_account_table():
    with sqlite3.Connection(DATABASE) as conn:
        cursor = conn.cursor()
        create_table = '''
        CREATE TABLE IF NOT EXISTS Accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bank TEXT NOT NULL,
        name TEXT NOT NULL,
        custom_name TEXT
        );
        '''
        cursor.execute(create_table)
        conn.commit()

def create_acc_snapshots():
    account_list = list_accounts()
    for account in account_list:
        try:
            get_snapshot_amount(account['id'], currentMonth)
        except:
            # https://stackoverflow.com/questions/9724906/python-date-of-the-previous-month
            print(f"account {account['id']} failed, creating snapshot")
            last_month = datetime.now() - dateutil.relativedelta.relativedelta(months=1)
            insert_into_snapshot(account['id'], currentMonth, get_current_balance(account['id'], last_month.strftime('%Y-%m')))
            pass

def create_transactions_table():
    # https://stackoverflow.com/questions/68694701/how-to-use-multiple-foreign-keys-in-one-table-in-sqlite
    with sqlite3.Connection(DATABASE) as conn:
        cursor = conn.cursor()
        create_table = '''
        CREATE TABLE IF NOT EXISTS Transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        account_id INTEGER NOT NULL,
        category_id INTEGER NOT NULL,
        description TEXT,
        debit INT DEFAULT 1 NOT NULL,
        amount REAL NOT NULL,
        FOREIGN KEY (account_id)
            REFERENCES Accounts (id),
        FOREIGN KEY (category_id)
            REFERENCES Categories (id)
        );
        '''
        cursor.execute(create_table)
        conn.commit()

def create_monthly_balance_table():
    with sqlite3.Connection(DATABASE) as conn:
        cursor = conn.cursor()
        create_table = '''
        CREATE TABLE IF NOT EXISTS snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER NOT NULL,
        snapshot_date TEXT NOT NULL,
        amount REAL NOT NULL,
        FOREIGN KEY (account_id)
            REFERENCES Accounts (id),
        UNIQUE (account_id, snapshot_date)
        );
        '''
        cursor.execute(create_table)
        conn.commit()

def create_bank_account(bank, name):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        insert_query = '''
        INSERT INTO Accounts (bank, name)
        VALUES (?, ?);
        '''
        # ten syntax ma zapobiegać sql injections??
        transaction_data = (bank, name)
        cursor.execute(insert_query, transaction_data)
        conn.commit()

def delete_bank_account(account_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        query = '''
                DELETE FROM Accounts WHERE id = ?;'''
        cursor.execute(query, [account_id])
        conn.commit()

def insert_into_snapshot(id, date, amount):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        insert_query = '''
        INSERT INTO snapshots (account_id, snapshot_date, amount)
        VALUES (?, ?, ?);
        '''

        transaction_data = (id, date, amount)
        cursor.execute(insert_query, transaction_data)
        conn.commit()

def update_snapshot(account_id, date, amount):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        insert_query = '''
        UPDATE snapshots SET amount = ?
        WHERE account_id = ? AND snapshot_date = ?
        '''
        transaction_data = (amount, account_id, date)
        cursor.execute(insert_query, transaction_data)
        conn.commit()

def db_exists():
    if Path(DATABASE).exists():
        return True

def create_dummy_data(flag):
    if flag:
        print("db exists")
        pass
    else:
        tx = Transactions()
        cs = Categories()
        cs.create_table()
        incoming = ["Wypka", "Kołchoz dodatkowe", "Other dodatkowe", "Odsetki"]
        fixed = ["Rent", "Electricity", "Gas", "Internet", "Phone"]
        var = ["Food", "Social", "Fun", "Shopping", "Kittens", "Bank expenses", "Learning", "Tickets"]
        planned = ["Trip", "Rain", "Investements", "Extra", "Emergency"]
        for i in incoming:
            cs.create_new_category(i, "I")
        for f in fixed:
            cs.create_new_category(f, "F")
        for v in var:
            cs.create_new_category(v, "V")
        for p in planned:
            cs.create_new_category(p, "P")
        create_bank_account("Purrun Bank", "Daily")
        create_bank_account("Kicion", "Daily")
        create_bank_account("Mollior", "Savings")
        create_bank_account("Leeroy", "Trip")
        #insert_transaction("2025-01-01", "Food", "biedra", 1, 50)
        tx.insert_new_transaction("2025-01-01", 1, 10, 50, description="biedra")
        tx.insert_new_transaction("2025-02-47", 2, 11, 13.50, description="date")
        #insert_transaction("2025-02-14", "Fun", "date", 2, 13.50)
        date = datetime.now().strftime("%Y-%m")
        insert_into_snapshot(1, date, 100)
        insert_into_snapshot(2, date, 100)
        insert_into_snapshot(3, date, 100)
        insert_into_snapshot(4, date, 100)
        print("dummy data created")

def create_db():
    flag = db_exists()
    create_account_table()
    create_transactions_table()
    create_monthly_balance_table()
    create_dummy_data(flag)