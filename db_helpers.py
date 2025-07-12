import sqlite3
from pathlib import Path

DATABASE = "test.db"

def insert_transaction(date, category, desc, bank, amount):

    # utwórz połączenie do test.db i zamknij po wykonaniu bloku
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        insert_query = '''
        INSERT INTO Transactions (timestamp, category, description, account, amount)
        VALUES (?, ?, ?, ?, ?);
        '''
        # ten syntax zapobiega sql injections
        transaction_data = (date, category, desc, bank, amount)
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

def add_new_account(bank, name, amount):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        insert_query = '''
        INSERT INTO Accounts (bank, name, amount)
        VALUES (?, ?, ?);
        '''
        transaction_data = (bank, name, amount)
        cursor.execute(insert_query, transaction_data)
        conn.commit()

def fetch_data_index():
    recent = fetch_from_db("select * from Transactions ORDER BY id DESC LIMIT 5")
    accounts = fetch_from_db("select bank, name, amount from Accounts")
    total = fetch_from_db("SELECT SUM(amount) FROM Accounts")
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

def list_accounts():
    return fetch_from_db("select id, bank from Accounts")

def sum_from_table(table, filter):
    # add validation
    query = f"SELECT SUM(amount) from {table} WHERE account = ?"
    sum = fetch_from_db(query, (filter,))
    return sum

def fetch_tr_details(id):
    query = "SELECT * from Transactions where id = ?"
    data = fetch_from_db(query, (id,))
    # wsadź do dictionary for easier jinja2 handling
    tr_data = [dict(row) for row in data]
    return tr_data

def update_transaction(new_data):
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

def create_account_table():
    with sqlite3.Connection(DATABASE) as conn:
        cursor = conn.cursor()
        create_table = '''
        CREATE TABLE IF NOT EXISTS Accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bank TEXT NOT NULL,
        name TEXT NOT NULL,
        custom_name TEXT,
        amount REAL NOT NULL
        );
        '''
        cursor.execute(create_table)
        conn.commit()

def create_transactions_table():
    with sqlite3.Connection(DATABASE) as conn:
        cursor = conn.cursor()
        create_table = '''
        CREATE TABLE IF NOT EXISTS Transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        account TEXT NOT NULL,
        category TEXT,
        description TEXT,
        debit INT DEFAULT 1 NOT NULL,
        amount REAL NOT NULL
        );
        '''
        cursor.execute(create_table)
        conn.commit()

def create_bank_account(bank, name, amount):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        insert_query = '''
        INSERT INTO Accounts (bank, name, amount)
        VALUES (?, ?, ?);
        '''
        # ten syntax ma zapobiegać sql injections??
        transaction_data = (bank, name, amount)
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
        create_bank_account("Purrun Bank", "Daily", 123.45)
        create_bank_account("Kicion", "Daily", 100.00)
        create_bank_account("Mollior", "Savings", 123.45)
        create_bank_account("Leeroy", "Trip", 0.00)
        insert_transaction("2025-01-01", "Food", "biedra", "Purrun Bank", 50)
        insert_transaction("2025-02-14", "Fun", "date", "Kicion", 13.50)
        print("dummy data created")

def create_db():
    flag = db_exists()
    create_account_table()
    create_transactions_table()
    create_dummy_data(flag)