import sqlite3, json

db = r'C:\DevopGodMode\runtime\temp\dgm_mat.db'
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print("TABLES:", tables)

# Schema of safe_action_queue
cur.execute("PRAGMA table_info(safe_action_queue)")
cols = cur.fetchall()
print("\nSCHEMA safe_action_queue:")
for c in cols: print(f"  {c['name']} {c['type']}")

# All records
cur.execute("SELECT * FROM safe_action_queue ORDER BY created_at DESC LIMIT 10")
rows = cur.fetchall()
print(f"\nRECORDS ({len(rows)}):")
for r in rows:
    d = dict(r)
    try: d['audit_trail'] = json.loads(d['audit_trail'])
    except: pass
    print(json.dumps(d, indent=2, default=str))

# events table
cur.execute("SELECT * FROM events ORDER BY rowid DESC LIMIT 5")
evts = cur.fetchall()
print(f"\nEVENTS ({len(evts)}):")
for e in evts: print(dict(e))

conn.close()
