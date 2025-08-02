import sqlite3
from pathlib import Path
from datetime import datetime
import dateutil.relativedelta

DATABASE = "test.db"
currentMonth = datetime.now().strftime("%Y-%m")

def insert_transaction(date, category, desc, account_id, amount):

    # utwórz połączenie do test.db i zamknij po wykonaniu bloku
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        insert_query = '''
        INSERT INTO Transactions (timestamp, category, description, account_id, amount)
        VALUES (?, ?, ?, ?, ?);
        '''
        # ten syntax zapobiega sql injections
        transaction_data = (date, category, desc, account_id, amount)
        cursor.execute(insert_query, transaction_data)
        conn.commit()

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

def update_table_row(table, column, new_value, filter):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        # ? syntax nie działa z nazwami tabel i kolumn - validate table and column with a whitelist?
        query = f"UPDATE {table} SET {column} = ? WHERE id = ?;"
        transaction_data = (new_value, filter)
        cursor.execute(query, transaction_data)
        conn.commit()

def delete_table_row(table, filter):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        # add validation thru whitelist for table
        query = f"DELETE FROM {table} WHERE id = ?;"
        # https://stackoverflow.com/questions/16856647/sqlite3-programmingerror-incorrect-number-of-bindings-supplied-the-current-sta
        cursor.execute(query, [filter])
        conn.commit()
    return

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

def fetch_tr_details(id):
    query = '''
            SELECT Transactions.id, Transactions.timestamp, 
                   Accounts.bank as bank, Accounts.name as name, 
                   Transactions.category, Transactions.description, 
                   Transactions.debit, Transactions.amount
            FROM Transactions 
            JOIN Accounts ON Transactions.account_id = Accounts.id 
            WHERE Transactions.id = ?
            '''
    data = fetch_from_db(query, (id,))
    # wsadź do dictionary for easier jinja2 handling
    tr_data = [dict(row) for row in data]
    return tr_data

def update_transaction(new_data):
    account_id = get_account_id(new_data['bank'], new_data['name'])
    print(f"account id is {account_id}")
    new_data['account_id'] = account_id
    new_data.pop('bank')
    new_data.pop('name')
    query = "UPDATE Transactions SET"
    for key, value in new_data.items():
        temp = (f"{key} = '{value}',")
        query = query + " " + temp
    
    # wywalenie ostatniego przecinka
    query = query[:-1] + f" WHERE id = {new_data['id']};"

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
    return

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
    with sqlite3.Connection(DATABASE) as conn:
        cursor = conn.cursor()
        create_table = '''
        CREATE TABLE IF NOT EXISTS Transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        account_id INTEGER NOT NULL,
        category TEXT,
        description TEXT,
        debit INT DEFAULT 1 NOT NULL,
        amount REAL NOT NULL,
        FOREIGN KEY (account_id)
            REFERENCES Accounts (id)
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
        create_bank_account("Purrun Bank", "Daily")
        create_bank_account("Kicion", "Daily")
        create_bank_account("Mollior", "Savings")
        create_bank_account("Leeroy", "Trip")
        insert_transaction("2025-01-01", "Food", "biedra", 1, 50)
        insert_transaction("2025-02-14", "Fun", "date", 2, 13.50)
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