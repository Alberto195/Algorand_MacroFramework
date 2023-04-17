import json

from algosdk import account, mnemonic
from algosdk.abi import Contract
from algosdk.atomic_transaction_composer import *
from macro.Mode import Mode


class AlgoClientBuilder:

    def __init__(self, creator_mnemonic, wallet_address, algod_address, algod_token, app_id=0):
        self.algod_client = None
        self.app_id = app_id
        self.creator_mnemonic = creator_mnemonic
        self.wallet_address = wallet_address
        self.algod_address = algod_address
        self.algod_token = algod_token

    def read_local_state(self):
        results = self.algod_client.account_info(self.wallet_address)
        for local_state in results["apps-local-state"]:
            if local_state["id"] == self.app_id:
                if "key-value" not in local_state:
                    return {}
                return self.format_state(local_state["key-value"])
        return {}

    # read app global state
    def read_global_state(self):
        results = self.algod_client.account_info(self.wallet_address)
        apps_created = results["created-apps"]
        for app in apps_created:
            if app["id"] == self.app_id:
                return self.format_state(app["params"]["global-state"])
        return {}

    # read variable state
    def read_variable_state(self, variable_name, mode):
        if mode == Mode.GLOBAL:
            formatted = self.read_global_state()
        else:
            formatted = self.read_local_state()

        val = None
        for key in formatted:
            if key == variable_name:
                val = formatted[key]
                break
        return val

    def format_state(self, state):
        formatted = {}
        for item in state:
            key = item["key"]
            value = item["value"]
            formatted_key = base64.b64decode(key).decode("utf-8")
            if value["type"] == 1:
                # byte string
                formatted_value = value["bytes"]
                formatted[formatted_key] = formatted_value
            else:
                # integer
                formatted[formatted_key] = value["uint"]
        return formatted

    # helper function to compile program source
    def compile_program(self, source_code):
        compile_response = self.algod_client.compile(source_code)
        return base64.b64decode(compile_response['result'])

    # helper function that converts a mnemonic passphrase into a private signing key
    def get_private_key_from_mnemonic(self, mn):
        private_key = mnemonic.to_private_key(mn)
        return private_key

    # create new application
    def create_app(self, private_key, approval_program, clear_program, global_schema, local_schema):
        # define sender as creator
        sender = account.address_from_private_key(private_key)

        # declare on_complete as NoOp
        on_complete = transaction.OnComplete.NoOpOC.real

        # get node suggested parameters
        params = self.algod_client.suggested_params()

        # create unsigned transaction
        txn = transaction.ApplicationCreateTxn(sender, params, on_complete,
                                               approval_program, clear_program,
                                               global_schema, local_schema)

        # sign transaction
        signed_txn = txn.sign(private_key)
        tx_id = signed_txn.transaction.get_txid()

        # send transaction
        self.algod_client.send_transactions([signed_txn])

        # wait for confirmation
        try:
            transaction_response = transaction.wait_for_confirmation(self.algod_client, tx_id, 4)
            print("TXID: ", tx_id)
            print("Result confirmed in round: {}".format(transaction_response['confirmed-round']))

        except Exception as err:
            print(err)
            return

        # display results
        transaction_response = self.algod_client.pending_transaction_info(tx_id)
        app_id = transaction_response['application-index']
        print("Created new app-id:", app_id)

        return app_id

    # call application
    def call_app(self, method_name, method_args: list):
        with open("./generated_code/teal/contract.json", "r") as f:
            js = json.load(f)
            contract = Contract.undictify(js)

        # define private keys
        private_key = self.get_private_key_from_mnemonic(self.creator_mnemonic)
        # get sender address
        sender = account.address_from_private_key(private_key)
        # create a Signer object
        signer = AccountTransactionSigner(private_key)

        # get node suggested parameters
        sp = self.algod_client.suggested_params()

        # Create an instance of AtomicTransactionComposer
        atc = AtomicTransactionComposer()
        atc.add_method_call(
            app_id=self.app_id,
            method=contract.get_method_by_name(method_name),
            sender=sender,
            sp=sp,
            signer=signer,
            method_args=method_args,
        )

        # send transaction
        results = atc.execute(self.algod_client, 2)

        # wait for confirmation
        print("TXID: ", results.tx_ids[0])
        print("Result confirmed in round: {}".format(results.confirmed_round))

    def init_algo_client(self):
        # initialize an algodClient
        self.algod_client = algod.AlgodClient(self.algod_token, self.algod_address)

    def init_app(self, local_ints, local_bytes, global_ints, global_bytes):
        # define private keys
        creator_private_key = self.get_private_key_from_mnemonic(self.creator_mnemonic)

        # configure schema
        global_schema = transaction.StateSchema(global_ints, global_bytes)
        local_schema = transaction.StateSchema(local_ints, local_bytes)

        # read approval and clear program from files
        with open("./generated_code/teal/approval.teal", "r") as f:
            approval_program = f.read()

        with open("./generated_code/teal/clear.teal", "r") as f:
            clear_program = f.read()

        # compile program to binary
        approval_program_compiled = self.compile_program(approval_program)

        # compile program to binary
        clear_state_program_compiled = self.compile_program(clear_program)

        self.app_id = self.create_app(
            creator_private_key,
            approval_program_compiled,
            clear_state_program_compiled,
            global_schema,
            local_schema,
        )
