from db_helpers import list_accounts, Transactions

def validate_bank_account(vendor, account_name):
    accounts = list_accounts()
    account_exists = False
    for acc in accounts:
        if vendor == acc['bank'] and account_name == acc['name']:
            account_exists = True

    return account_exists

trans = Transactions()
#trans.insert_new_transaction("2025-08", 2, 21.37, category='Fun', description='Fun transaction')

trans.update_transaction(12, timestamp="2025-10-15")






