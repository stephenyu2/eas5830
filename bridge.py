from web3 import Web3
from web3.providers.rpc import HTTPProvider
from web3.middleware import ExtraDataToPOAMiddleware #Necessary for POA chains
from datetime import datetime
import json
import pandas as pd


def connect_to(chain):
    if chain == 'source':  # The source contract chain is avax
        api_url = f"https://api.avax-test.network/ext/bc/C/rpc" #AVAX C-chain testnet

    if chain == 'destination':  # The destination contract chain is bsc
        api_url = f"https://data-seed-prebsc-1-s1.binance.org:8545/" #BSC testnet

    if chain in ['source','destination']:
        w3 = Web3(Web3.HTTPProvider(api_url))
        # inject the poa compatibility middleware to the innermost layer
        w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    return w3


def get_contract_info(chain, contract_info):
    """
        Load the contract_info file into a dictionary
        This function is used by the autograder and will likely be useful to you
    """
    try:
        with open(contract_info, 'r')  as f:
            contracts = json.load(f)
    except Exception as e:
        print( f"Failed to read contract info\nPlease contact your instructor\n{e}" )
        return 0
    return contracts[chain]



def scan_blocks(chain, contract_info="contract_info.json"):
    """
        chain - (string) should be either "source" or "destination"
        Scan the last 5 blocks of the source and destination chains
        Look for 'Deposit' events on the source chain and 'Unwrap' events on the destination chain
        When Deposit events are found on the source chain, call the 'wrap' function the destination chain
        When Unwrap events are found on the destination chain, call the 'withdraw' function on the source chain
    """

    # This is different from Bridge IV where chain was "avax" or "bsc"
    if chain not in ['source','destination']:
        print( f"Invalid chain: {chain}" )
        return 0
    
    contracts = get_contract_info(chain, contract_info)
    w3 = connect_to(chain)

    warden_address = Web3.to_checksum_address(contracts["warden"]["address"])
    warden_key = contracts["warden"]["private_key"]

    source_info = contracts["source"]
    dest_info = contracts["destination"]

    source_contract = connect_to("source").eth.contract(
        address=Web3.to_checksum_address(source_info["address"]),
        abi=source_info["abi"]
    )
    dest_contract = connect_to("destination").eth.contract(
        address=Web3.to_checksum_address(dest_info["address"]),
        abi=dest_info["abi"]
    )

    if chain == "source":
        w3s = connect_to("source")
        end_block = w3s.eth.get_block_number()
        start_block = end_block - 5
        event_filter = source_contract.events.Deposit.create_filter(from_block=start_block,to_block=end_block,argument_filters={})
        events = event_filter.get_all_entries()
        w3d = connect_to("destination")
        for evt in events:
            token = evt.args["token"]
            recipient = evt.args["recipient"]
            amount = evt.args["amount"]
            nonce = w3d.eth.get_transaction_count(warden_address)
            tx = dest_contract.functions.wrap(token, recipient, amount).build_transaction({
                "from": warden_address,
                "nonce": nonce,
                "gas": 500000,
                "gasPrice": w3d.eth.gas_price
            })
            signed = w3d.eth.account.sign_transaction(tx, private_key=warden_key)
            w3d.eth.send_raw_transaction(signed.rawTransaction)

    if chain == "destination":
        w3d = connect_to("destination")
        end_block = w3d.eth.get_block_number()
        start_block = end_block - 5
        event_filter = dest_contract.events.Unwrap.create_filter(from_block=start_block,to_block=end_block,argument_filters={})
        events = event_filter.get_all_entries()
        w3s = connect_to("source")
        for evt in events:
            token = evt.args["underlying_token"]
            recipient = evt.args["to"]
            amount = evt.args["amount"]
            nonce = w3s.eth.get_transaction_count(warden_address)
            tx = source_contract.functions.withdraw(token, recipient, amount).build_transaction({
                "from": warden_address,
                "nonce": nonce,
                "gas": 500000,
                "gasPrice": w3s.eth.gas_price
            })
            signed = w3s.eth.account.sign_transaction(tx, private_key=warden_key)
            w3s.eth.send_raw_transaction(signed.rawTransaction)
