from web3 import Web3
from web3.providers.rpc import HTTPProvider
import requests
import json

bayc_address = "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"
contract_address = Web3.to_checksum_address(bayc_address)

# You will need the ABI to connect to the contract
# The file 'abi.json' has the ABI for the bored ape contract
# In general, you can get contract ABIs from etherscan
# https://api.etherscan.io/api?module=contract&action=getabi&address=0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D
with open('ape_abi.json', 'r') as f:
    abi = json.load(f)

############################
# Connect to an Ethereum node
api_url = "https://mainnet.infura.io/v3/36ae5171512d47b8a2eb74cdfdfa2cb4"  # YOU WILL NEED TO PROVIDE THE URL OF AN ETHEREUM NODE
provider = HTTPProvider(api_url)
web3 = Web3(provider)

def get_from_ipfs(cid,content_type="json"):
	assert isinstance(cid,str), f"get_from_ipfs accepts a cid in the form of a string"
	#YOUR CODE HERE	
	url = f"https://gateway.pinata.cloud/ipfs/{cid}"
	response = requests.get(url, timeout=60)
	data = response.json()
	assert isinstance(data,dict), f"get_from_ipfs should return a dict"
	return data


def get_ape_info(ape_id):
    assert isinstance(ape_id, int), f"{ape_id} is not an int"
    assert 0 <= ape_id, f"{ape_id} must be at least 0"
    assert 9999 >= ape_id, f"{ape_id} must be less than 10,000"

    data = {'owner': "", 'image': "", 'eyes': ""}

    # YOUR CODE HERE
    bayc_contract = web3.eth.contract(address = contract_address, abi = abi)
    data['owner'] = bayc_contract.functions.ownerOf(ape_id).call()
    data['image'] = bayc_contract.functions.tokenURI(ape_id).call()
    bayc_data = get_from_ipfs(data['image'])
    data['eyes'] = next((a["value"] for a in bayc_data["attributes"] if a["trait_type"] == "Eyes"), None)


    assert isinstance(data, dict), f'get_ape_info{ape_id} should return a dict'
    assert all([a in data.keys() for a in
                ['owner', 'image', 'eyes']]), f"return value should include the keys 'owner','image' and 'eyes'"
    return data
