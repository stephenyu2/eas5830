from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from eth_account import Account
import json


def connect_to(chain):
    if chain == "source":  # The source contract chain is avax
        api_url = "https://api.avax-test.network/ext/bc/C/rpc"  # AVAX C-chain testnet
    elif chain == "destination":  # The destination contract chain is bsc
        api_url = "https://data-seed-prebsc-1-s1.binance.org:8545/"  # BSC testnet
    else:
        raise ValueError(f"Invalid chain: {chain}")

    w3 = Web3(Web3.HTTPProvider(api_url))
    # Necessary for POA chains (both these testnets)
    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    return w3


def scan_blocks(chain, contract_info="contract_info.json"):
    """
    chain - (string) should be either "source" or "destination"

    Scan recent blocks:
      - For chain == "source": look for Deposit events on the source chain,
        and call wrap() on the destination chain.
      - For chain == "destination": look for Unwrap events on the destination
        chain, and call withdraw() on the source chain.
    """

    if chain not in ["source", "destination"]:
        print(f"Invalid chain: {chain}")
        return 0

    # Load contract info
    with open(contract_info, "r") as f:
        contracts = json.load(f)

    # Derive warden address from private key (avoid mismatch)
    warden_key = contracts["warden"]["private_key"]
    warden_acct = Account.from_key(warden_key)
    warden_address = warden_acct.address

    source_info = contracts["source"]
    dest_info = contracts["destination"]

    # Connect to both chains
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

    # How many blocks back to scan (20 is much safer than 5)
    if chain == "source":
        end_block = w3s.eth.get_block_number()
        start_block = max(0, end_block - 20)

        # Find Deposit events on the source chain
        event_filter = source_contract.events.Deposit.create_filter(
            from_block=start_block,
            to_block=end_block,
            argument_filters={},
        )
        events = event_filter.get_all_entries()

        # Use a single nonce and increment for multiple transactions
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
                    "gas": 500_000,
                    "gasPrice": w3d.eth.gas_price,
                }
            )
            nonce += 1

            signed = warden_acct.sign_transaction(tx)
            w3d.eth.send_raw_transaction(signed.raw_transaction)

    if chain == "destination":
        end_block = w3d.eth.get_block_number()
        start_block = max(0, end_block - 20)

        # Find Unwrap events on the destination chain
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
                    "gas": 500_000,
                    "gasPrice": w3s.eth.gas_price,
                }
            )
            nonce += 1

            signed = warden_acct.sign_transaction(tx)
            w3s.eth.send_raw_transaction(signed.raw_transaction)