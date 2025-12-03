from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from eth_account import Account
import json


def connect_to(chain):
    if chain == 'source':  # The source contract chain is avax
        api_url = "https://api.avax-test.network/ext/bc/C/rpc"  # AVAX C-chain testnet
    elif chain == 'destination':  # The destination contract chain is bsc
        api_url = "https://data-seed-prebsc-1-s1.binance.org:8545/"  # BSC testnet
    else:
        raise ValueError(f"Invalid chain: {chain}")

    w3 = Web3(Web3.HTTPProvider(api_url))
    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    return w3


def scan_blocks(chain, contract_info="contract_info.json"):
    """
    chain - (string) should be either "source" or "destination"
    Scan the last 5 blocks of the source and destination chains
    Look for 'Deposit' events on the source chain and 'Unwrap' events on the destination chain
    When Deposit events are found on the source chain, call the 'wrap' function on the destination chain
    When Unwrap events are found on the destination chain, call the 'withdraw' function on the source chain
    """

    if chain not in ["source", "destination"]:
        print(f"Invalid chain: {chain}")
        return 0

    with open(contract_info, "r") as f:
        contracts = json.load(f)

    # Derive warden address from private key to avoid mismatch
    warden_key = contracts["warden"]["private_key"]
    warden_acct = Account.from_key(warden_key)
    warden_address = warden_acct.address

    source_info = contracts["source"]
    dest_info = contracts["destination"]

    w3s = connect_to("source")
    w3d = connect_to("destination")

    source_contract = w3s.eth.contract(
        address=Web3.to_checksum_address(source_info["address"]),
        abi=source_info["abi"],
    )
    dest_contract = w3d.eth.contract(
        address=Web3.to_checksum_address(dest_info["address"]),
        abi=dest_info["abi"],
    )

    if chain == "source":
        end_block = w3s.eth.get_block_number()
        start_block = max(0, end_block - 5)

        event_filter = source_contract.events.Deposit.create_filter(
            from_block=start_block,
            to_block=end_block,
            argument_filters={},
        )
        events = event_filter.get_all_entries()

        # Get starting nonce once and increment per tx
        nonce = w3d.eth.get_transaction_count(warden_address)

        for evt in events:
            token = evt.args["token"]
            recipient = evt.args["recipient"]
            amount = evt.args["amount"]

            tx = dest_contract.functions.wrap(
                token, recipient, amount
            ).build_transaction(
                {
                    "from": warden_address,
                    "nonce": nonce,
                    "gas": 500000,
                    "gasPrice": w3d.eth.gas_price,
                }
            )
            nonce += 1  # increment for next tx

            signed = warden_acct.sign_transaction(tx)
            w3d.eth.send_raw_transaction(signed.raw_transaction)

    if chain == "destination":
        end_block = w3d.eth.get_block_number()
        start_block = max(0, end_block - 5)

        event_filter = dest_contract.events.Unwrap.create_filter(
            from_block=start_block,
            to_block=end_block,
            argument_filters={},
        )
        events = event_filter.get_all_entries()

        nonce = w3s.eth.get_transaction_count(warden_address)

        for evt in events:
            token = evt.args["underlying_token"]
            recipient = evt.args["to"]
            amount = evt.args["amount"]

            tx = source_contract.functions.withdraw(
                token, recipient, amount
            ).build_transaction(
                {
                    "from": warden_address,
                    "nonce": nonce,
                    "gas": 500000,
                    "gasPrice": w3s.eth.gas_price,
                }
            )
            nonce += 1

            signed = warden_acct.sign_transaction(tx)
            w3s.eth.send_raw_transaction(signed.raw_transaction)