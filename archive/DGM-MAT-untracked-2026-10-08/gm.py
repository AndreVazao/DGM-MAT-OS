import urllib.request, json
r = urllib.request.urlopen('http://127.0.0.1:8181/runtime/missions', timeout=5)
print(json.dumps(json.loads(r.read().decode()), indent=2))
