import json
import base64
from algosdk import account
from algosdk.v2client import algod
from algosdk.future import transaction
import time


# # This is a complete code example that:
# #   1. Create a new test account
# #   2. Ask to fund your created account
# #   3. Send 1 Algo to TestNet faucet address (HZ57J3K46JIJXILONBBZOHX6BKPXEM2VVXNRFSUED6DKFD5ZD24PMJ3MVA) with the note "Hello World".


def getting_started_example():
    # Using Rand Labs Developer API
    # see https://github.com/algorand/py-algorand-sdk/issues/169
    # Change algod_token and algod_address to connect to a different client
    # algod_token = "2f3203f21e738a1de6110eba6984f9d03e5a95d7a577b34616854064cf2c0e7b"
    # algod_address = "https://academy-algod.dev.aws.algodev.network/"
    # algod_address = "http://hackathon.algodev.network:9100"
    # algod_token = "ef920e2e7e002953f4b29a8af720efe8e4ecc75ff102b165e0472834b25832c1"
    algod_address = "http://hackathon.algodev.network:9100"
    algod_token = "ef920e2e7e002953f4b29a8af720efe8e4ecc75ff102b165e0472834b25832c1"

    algod_client = algod.AlgodClient(algod_token, algod_address)

    # Generate new account for this transaction
    secret_key, my_address = account.generate_account()

    print("My address: {}".format(my_address))

    # Check your balance. It should be 0 microAlgos

    account_info = algod_client.account_info(my_address)
    print("Account balance: {} microAlgos".format(account_info.get('amount')) + "\n")

    # Fund the created account
    print(
        'Fund the created account using testnet faucet: \n https://dispenser.testnet.aws.algodev.network/?account=' + format(
            my_address))

    completed = ""
    while completed.lower() != 'yes':
        completed = input("Type 'yes' once you funded the account: ");

    print('Fund transfer in process...')
    # Wait for the faucet to transfer funds
    time.sleep(10)

    print('Fund transferred!')
    # Check your balance. It should be 5000000 microAlgos
    account_info = algod_client.account_info(my_address)
    print("Account balance: {} microAlgos".format(account_info.get('amount')) + "\n")

    # build transaction
    print("Building transaction")
    params = algod_client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    # params.flat_fee = True
    # params.fee = 1000
    receiver = "HZ57J3K46JIJXILONBBZOHX6BKPXEM2VVXNRFSUED6DKFD5ZD24PMJ3MVA"
    note = "Hello World".encode()
    amount = 100000
    closeto = "HZ57J3K46JIJXILONBBZOHX6BKPXEM2VVXNRFSUED6DKFD5ZD24PMJ3MVA"
    # Fifth argument is a close_remainder_to parameter that creates a payment txn that sends all of the remaining funds to the specified address. If you want to learn more, go to: https://developer.algorand.org/docs/reference/transactions/#payment-transaction
    unsigned_txn = transaction.PaymentTxn(my_address, params, receiver, amount, closeto, note)

    # sign transaction
    print("Signing transaction")
    signed_txn = unsigned_txn.sign(secret_key)
    print("Sending transaction")
    txid = algod_client.send_transaction(signed_txn)
    print('Transaction Info:')
    print("Signed transaction with txID: {}".format(txid))

    # wait for confirmation
    try:
        print("Waiting for confirmation")
        confirmed_txn = transaction.wait_for_confirmation(algod_client, txid, 4)
    except Exception as err:
        print(err)
        return
    print("txID: {}".format(txid), " confirmed in round: {}".format(confirmed_txn.get("confirmed-round", 0)))
    print("Transaction information: {}".format(
        json.dumps(confirmed_txn, indent=4)))
    print("Decoded note: {}".format(base64.b64decode(
        confirmed_txn["txn"]["txn"]["note"]).decode()))
    print("Starting Account balance: {} microAlgos".format(account_info.get('amount')))
    print("Amount transfered: {} microAlgos".format(amount))
    print("Fee: {} microAlgos".format(params.min_fee))
    closetoamt = account_info.get('amount') - (params.min_fee + amount)
    print("Close to Amount: {} microAlgos".format(closetoamt) + "\n")

    account_info = algod_client.account_info(my_address)
    print("Final Account balance: {} microAlgos".format(account_info.get('amount')) + "\n")


getting_started_example()
