import urllib.request, json, time

def get(path):
    r = urllib.request.urlopen(f'http://127.0.0.1:8181{path}', timeout=5)
    return json.loads(r.read().decode())

print("=== T+0 ===")
print("QUEUE:", json.dumps(get('/runtime/queue'), indent=2))
print("MISSIONS:", json.dumps(get('/runtime/missions'), indent=2))

time.sleep(30)
print("\n=== T+30s ===")
print("QUEUE:", json.dumps(get('/runtime/queue'), indent=2))
print("MISSIONS:", json.dumps(get('/runtime/missions'), indent=2))

time.sleep(30)
print("\n=== T+60s ===")
print("QUEUE:", json.dumps(get('/runtime/queue'), indent=2))
print("MISSIONS:", json.dumps(get('/runtime/missions'), indent=2))

time.sleep(30)
print("\n=== T+90s ===")
print("QUEUE:", json.dumps(get('/runtime/queue'), indent=2))
print("MISSIONS:", json.dumps(get('/runtime/missions'), indent=2))

time.sleep(30)
print("\n=== T+120s ===")
print("QUEUE:", json.dumps(get('/runtime/queue'), indent=2))
print("MISSIONS:", json.dumps(get('/runtime/missions'), indent=2))
