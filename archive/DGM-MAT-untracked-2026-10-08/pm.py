import urllib.request
import json

url = 'http://127.0.0.1:8181/runtime/missions'
payload = {'goal': 'runtime activation test', 'description': 'fase 43.3 probe'}
data = json.dumps(payload).encode('utf-8')
headers = {'Content-Type': 'application/json'}
req = urllib.request.Request(url, data=data, headers=headers, method='POST')
try:
    resp = urllib.request.urlopen(req, timeout=15)
    print('STATUS:', resp.status)
    print('BODY:', resp.read().decode('utf-8'))
except Exception as e:
    print('ERROR:', type(e).__name__, str(e))
