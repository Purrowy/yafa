from db_helpers import list_accounts, Transactions, Snapshot, Accounts
import json

def validate_bank_account(vendor, account_name):
    accounts = list_accounts()
    account_exists = False
    for acc in accounts:
        if vendor == acc['bank'] and account_name == acc['name']:
            account_exists = True

    return account_exists

#trans = Transactions()
#trans.insert_new_transaction("2025-08", 2, 21.37, category='Fun', description='Fun transaction')

#trans.update_transaction(12, timestamp="2025-10-15")

snp = Snapshot()
#snp.create_table()
#list_data = [{'id': 1, 'bank': 'aaa', 'amount': 100}, {'id': 2, 'bank': 'Kicion', 'amount': 2137}]
#snp.create_snapshot(list_data)
# print("---")
# last =  snp.get_last_snapshot()
# print(last)
# print("^ z get last snap")
acs = Accounts()
amount = acs.get_account_balance(2)
print(f"---\n{amount}\n^z get acc balance")



