import sqlite3
import json
from pathlib import Path
from datetime import datetime

DATABASE = "test.db"
currentMonth = datetime.now().strftime("%Y-%m")


class Snapshot:
    def __init__(self, db_path=DATABASE):
        self.db_path = db_path

    def create_snapshot(self):

        acs = Accounts()
        timestamp = datetime.now()

        accounts = acs.get_accounts()

        # pop unneeded items from each list
        # calculate current balance for each acc and add it to the list of dicts.
        # Set amount to 0 if get_acc_balance doesn't return anything
        for account in accounts:
            account.pop("name")
            account.pop("bank")
            try:
                account['amount'] = acs.get_account_balance(account['id'])
            except:
                account['amount'] = 0

        # change to JSON and insert as is to data column in Snapshots table
        json_data = json.dumps(accounts)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = '''INSERT INTO Snapshots (timestamp, data) VALUES (?, ?)'''
            cursor.execute(query, (timestamp, json_data))
            conn.commit()
            cursor.close()

        pass

    def get_last_snapshot(self):

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = '''SELECT timestamp, data FROM Snapshots ORDER BY timestamp DESC LIMIT 1'''
            cursor.execute(query)
            result = cursor.fetchone()
            timestamp, data = result
            cursor.close()

        # zwróc jako dict
        return {
            'timestamp': timestamp,
            'data': json.loads(data)
        }

    def create_table(self):
        print("create_table called db")
        with sqlite3.Connection(self.db_path) as conn:
            cursor = conn.cursor()
            create_table = '''
            CREATE TABLE IF NOT EXISTS Snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL UNIQUE,
            data JSON NOT NULL
            );
            '''
            cursor.execute(create_table)
            conn.commit()

class Accounts:
    def __init__(self, db_path=DATABASE):
        self.db_path = db_path

    def create_table(self):
        with sqlite3.Connection(self.db_path) as conn:
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

    def get_account_balance(self, account_id):

        # 1. wczytaj dane z last snap
        snp = Snapshot(self.db_path)
        last_snapshot = snp.get_last_snapshot()
        last_snapshot_timestamp = last_snapshot['timestamp']

        # 2. z last snap wczytaj wartość pod amount, używając account id
        try:
            last_balance = next(item['amount'] for item in last_snapshot['data'] if item['id'] == account_id)
        except:
            last_balance = 0
        #print(f"Get account balance:\nlast_snapshot_timestamp: {last_snapshot_timestamp}\nlast balance loaded: {last_balance}")

        # 3. znajdź sumę transakcji późniejszych od last_snap_date dla danego account_id z Transactions
        tx = Transactions()
        sum_of_trs_since_last_snapshot = tx.sum_transactions_by_account(account_id, last_snapshot_timestamp)
        #print(f"sum of last trx loaded: {sum_of_trs_since_last_snapshot}")

        # move it to sum_trs later
        if sum_of_trs_since_last_snapshot is None:
            sum_of_trs_since_last_snapshot = 0

        # 4. oblicz current balance
        current_balance = last_balance - sum_of_trs_since_last_snapshot
        #print(f"current_balance: {current_balance} for account_id: {account_id}")

        return current_balance

    def get_account_id(self, bank, name):
        try:
            # https://stackoverflow.com/questions/30294515/converting-sqlite3-cursor-to-int-python
            con = sqlite3.connect(self.db_path)
            con.row_factory = sqlite3.Row
            cursor = con.cursor()
            query = "SELECT id FROM Accounts WHERE bank = ? AND name = ?"
            cursor.execute(query, (bank, name,))
            account_id = cursor.fetchone()[0]
            return account_id
        except:
            return False

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

    def create_table(self):
        # https://stackoverflow.com/questions/68694701/how-to-use-multiple-foreign-keys-in-one-table-in-sqlite
        with sqlite3.Connection(self.db_path) as conn:
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

    # get_transactions and get_all should be combined into one and reworked
    def get_transaction(self, transaction_id, mode="default"):
        with sqlite3.connect(self.db_path) as conn:
            # bez sqlite3.Row nie działa transaction.keys()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            match mode:
                case "default":
                    query = "SELECT * FROM Transactions WHERE id = ?"
                case "dash":
                    query = '''
                            SELECT Transactions.id as id, timestamp, Accounts.bank as account, description, amount
                            FROM Transactions
                            JOIN Accounts ON Transactions.account_id = Accounts.id
                            ORDER BY Transactions.id DESC LIMIT 5
                            '''
                    cursor.execute(query)
                    transactions = cursor.fetchall()
                    return transactions
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
            transactions = cursor.fetchone()
            return transactions

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

    def sum_transactions_by_account(self,account_id, start_time):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = '''
                    SELECT SUM(Transactions.amount) as total from Transactions 
                    WHERE Transactions.account_id = ?
                    AND Transactions.timestamp > ?
                    '''
            cursor.execute(query, (account_id, start_time))
            rows = cursor.fetchone()

        return rows[0]

def update_account_name(account_id, new_name):
    query = "UPDATE Accounts SET name = ? WHERE id = ?;"
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (new_name, account_id, ))
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

def db_exists():
    if Path(DATABASE).exists():
        return True

def create_dummy_data(flag):
    if flag:
        print("db exists")
        return
    else:
        tx = Transactions()
        cs = Categories()
        snp = Snapshot()

        incoming = ["Wypka", "Kołchoz dodatkowe", "Other dodatkowe", "Odsetki"]
        fixed = ["Rent", "Electricity", "Gas", "Internet", "Phone"]
        var = ["Food", "Social", "Fun", "Shopping", "Kittens", "Bank expenses", "Learning", "Tickets"]
        planned = ["Trip", "Rain", "Investments", "Extra", "Emergency"]
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

        tx.insert_new_transaction("2025-01-01", 1, 10, 50, description="biedra")
        tx.insert_new_transaction("2025-02-47", 2, 11, 13.50, description="date")

        snp.create_snapshot()
        print("dummy data created")

def create_db():
    flag = db_exists()

    acs = Accounts()
    cs = Categories()
    snp = Snapshot()
    tx = Transactions()

    acs.create_table()
    cs.create_table()
    snp.create_table()
    tx.create_table()

    create_dummy_data(flag)