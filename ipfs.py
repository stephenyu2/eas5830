import requests
import json

def pin_to_ipfs(data):
	assert isinstance(data,dict), f"Error pin_to_ipfs expects a dictionary"
	#YOUR CODE HERE
	pinata_api = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySW5mb3JtYXRpb24iOnsiaWQiOiIwNjFiZTdiNC02OTRlLTQyZTEtYTlhMC0yNGM0MjRiMjFkNjEiLCJlbWFpbCI6InNweXUyNkBzZWFzLnVwZW5uLmVkdSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJwaW5fcG9saWN5Ijp7InJlZ2lvbnMiOlt7ImRlc2lyZWRSZXBsaWNhdGlvbkNvdW50IjoxLCJpZCI6IkZSQTEifSx7ImRlc2lyZWRSZXBsaWNhdGlvbkNvdW50IjoxLCJpZCI6Ik5ZQzEifV0sInZlcnNpb24iOjF9LCJtZmFfZW5hYmxlZCI6ZmFsc2UsInN0YXR1cyI6IkFDVElWRSJ9LCJhdXRoZW50aWNhdGlvblR5cGUiOiJzY29wZWRLZXkiLCJzY29wZWRLZXlLZXkiOiJmOTYyNzNjNWY0YWM0N2M0ZTY1ZSIsInNjb3BlZEtleVNlY3JldCI6Ijg0ZmRiMzdkODIyY2EyOWI0YTIwNTgxZWU1NmRmY2ZmNDBmZmJkYjE4NDkwMzAwMGNkNmRiNDRkMTc0YmFkNzAiLCJleHAiOjE3OTMwNjU3MzZ9.Taeg_q7OhtdS0C3Xon9qdEDGKhkgs_I6dgPnJiNEn10"
	url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
	headers = {
		"Authorization": pinata_api,
		"Content-Type": "application/json"
	}
	response = requests.post(url, headers=headers, json=data, timeout=60)
	print("Status code:", response.status_code)
	print("Response text:", response.text)
	response.raise_for_status()
	cid = response.json()["IpfsHash"]
	return cid

def get_from_ipfs(cid,content_type="json"):
	assert isinstance(cid,str), f"get_from_ipfs accepts a cid in the form of a string"
	#YOUR CODE HERE	

	assert isinstance(data,dict), f"get_from_ipfs should return a dict"
	return data

if __name__ == "__main__":
	sample = {"class": "EAS5830", "msg": "Testing IPFS"}
	cid = pin_to_ipfs(sample)
	print("✅ Pinned CID:", cid)
	data = get_from_ipfs(cid)
	print("Fetched back:", data)
