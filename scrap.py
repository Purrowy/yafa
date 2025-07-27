from db_helpers import list_accounts

def validate_bank_account(vendor, account_name):
    accounts = list_accounts()
    account_exists = False
    for acc in accounts:
        if vendor == acc['bank'] and account_name == acc['name']:
            account_exists = True

    return account_exists





