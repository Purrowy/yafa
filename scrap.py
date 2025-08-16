from db_helpers import Transactions, Accounts, Categories

tx = Transactions()
acs = Accounts()
cs = Categories()

def get_dashboard_data():
    categories = cs.list_categories()
    total = 0
    # can either calculate balance each time or load data from last snapshot
    accounts = acs.get_accounts()
    for account in accounts:
        account['amount'] = acs.get_account_balance(account['id'])
        total += account['amount']

    recent_transactions = tx.get_transaction(1, "dash")

    return accounts, total, recent_transactions, categories

#trans = Transactions()
#trans.insert_new_transaction("2025-08", 2, 21.37, category='Fun', description='Fun transaction')

#trans.update_transaction(12, timestamp="2025-10-15")

#snp = Snapshot()
#snp.create_table()
#list_data = [{'id': 1, 'bank': 'aaa', 'amount': 100}, {'id': 2, 'bank': 'Kicion', 'amount': 2137}]
#snp.create_snapshot(list_data)
# print("---")
# last =  snp.get_last_snapshot()
# print(last)
# print("^ z get last snap")
#acs = Accounts()
#amount = acs.get_account_balance(2)
#print(f"---\n{amount}\n^z get acc balance")



