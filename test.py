import requests

transactions = [
    { "payer": "DANNON", "points": 1000, "timestamp": "2020-11-02T14:00:00Z" },
    { "payer": "UNILEVER", "points": 200, "timestamp": "2020-10-31T11:00:00Z" },
    { "payer": "DANNON", "points": -200, "timestamp": "2020-10-31T15:00:00Z" },
    { "payer": "MILLER COORS", "points": 10000, "timestamp": "2020-11-01T14:00:00Z" },
    { "payer": "DANNON", "points": 300, "timestamp": "2020-10-31T10:00:00Z" }
]

for tn in transactions:
    resp = requests.post('http://localhost:5000/add_transaction', data=tn)
    if resp.status_code != 200:
        print("Something went wrong (%d, %s)" % (resp.status_code, resp.text))

resp = requests.get('http://localhost:5000/balances')
print(resp.status_code, resp.text)

resp = requests.post("http://localhost:5000/spend", { "points": 5000 })
print(resp.status_code, resp.text)

resp = requests.get('http://localhost:5000/balances')
print(resp.status_code, resp.text)