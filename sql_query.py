import sqlite3
import os
from pathlib import Path

DATABASE = "test.db"

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

def create_dummy_accs():
    if db_exists():
        pass
    else:
        create_bank_account("Purrun Bank", "Daily", 123.45)
        create_bank_account("Kicion", "Daily", 100.00)
        create_bank_account("Mollior", "Savings", 123.45)
        create_bank_account("Leeroy", "Trip", 0.00)

def create_db():
    create_account_table()
    create_transactions_table()
    create_dummy_accs()