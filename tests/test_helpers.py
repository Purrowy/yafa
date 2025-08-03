import sqlite3
from os import abort
from robot.api.deco import keyword

DATABASE = "../test.db"
current_month = "2025-08"
last_month = "2025-07"

def clean_db():

    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("DELETE FROM Transactions")
        c.execute("DELETE FROM Accounts")
        c.execute("DELETE FROM snapshots")
        c.execute("DELETE FROM sqlite_sequence")
        conn.commit()
        conn.close()
    except:
        print("could not clean db")
        abort()

def insert_account(bank_name, account_name):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("INSERT INTO Accounts (bank, name) VALUES (?, ?)", (bank_name, account_name))
    conn.commit()
    conn.close()

def insert_snapshot(account_id, snapshot_date, amount):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        insert_query = '''
        INSERT INTO snapshots (account_id, snapshot_date, amount)
        VALUES (?, ?, ?);
        '''

        transaction_data = (account_id, snapshot_date, amount)
        cursor.execute(insert_query, transaction_data)
        conn.commit()

def insert_transaction(date, category, desc, account_id, amount):

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        insert_query = '''
        INSERT INTO Transactions (timestamp, category, description, account_id, amount)
        VALUES (?, ?, ?, ?, ?);
        '''
        transaction_data = (date, category, desc, account_id, amount)
        cursor.execute(insert_query, transaction_data)
        conn.commit()

def app_start_tc():

    clean_db()

    insert_account("Acc1", "TC1")
    insert_account("Acc2", "TC2")
    insert_account("Acc3", "TC3")
    insert_account("Acc4", "TC4")

    insert_snapshot(1, current_month, 75)
    insert_snapshot(3, current_month, 100)
    insert_snapshot(1, last_month, 100)
    insert_snapshot(2, last_month, 50)

    insert_transaction(last_month, "Test", "test", 1, 25)
    insert_transaction(last_month, "Test", "test", 2, 25)


print(">>>im here<<<")
app_start_tc()