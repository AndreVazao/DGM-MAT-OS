import sys, os, time, json, sqlite3
from datetime import datetime

sys.path.insert(0, r'C:\ProgramasGodMode\DGM-MAT')
os.chdir(r'C:\ProgramasGodMode\DGM-MAT')

DB_PATH = r'C:\DevopGodMode\runtime\temp\dgm_mat.db'
LOG_PATH = r'C:\DevopGodMode\runtime\logs\dgm-runtime.log'
MISSIONS_PATH = r'C:\DevopGodMode\runtime\missions'

def db_snapshot():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT id,action_type,status,is_approved,approved_by,error_message,audit_trail FROM safe_action_queue WHERE id=1")
    row = dict(cur.fetchone())
    row['audit_trail'] = json.loads(row['audit_trail'])
    cur.execute("SELECT COUNT(*) as cnt FROM events")
    row['event_count'] = cur.fetchone()['cnt']
    conn.close()
    return row

def log_tail(n=5):
    try:
        with open(LOG_PATH, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
        return [l.rstrip() for l in lines[-n:]]
    except:
        return []

def mission_snapshot():
    path = os.path.join(MISSIONS_PATH, 'mission_4521fd1d.json')
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return None

def stamp(label):
    print(f"\n{'='*60}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {label}")
    print('='*60)

# ---- T-0: baseline ----
stamp("BASELINE — antes de aprovação")
print("DB:", json.dumps(db_snapshot(), indent=2))
m = mission_snapshot()
print("MISSION status:", m['status'] if m else "NOT FOUND")
print("LOG tail:", log_tail(3))

# ---- APROVAÇÃO ----
stamp("APROVAÇÃO MANUAL — action_id=1")
from core.runtime.safe_action_queue import SafeActionQueue
queue = SafeActionQueue()
print("Queue instance:", id(queue))
print("Handlers before:", list(queue._handlers.keys()))
print("Worker alive:", queue._worker_thread.is_alive() if queue._worker_thread else False)

queue.approve(1, operator="fase_43_4_force")
print("approve() called — action_id=1, operator=fase_43_4_force")

# ---- T+2s ----
time.sleep(2)
stamp("T+2s — imediatamente após approve()")
print("DB:", json.dumps(db_snapshot(), indent=2))
print("LOG tail:", log_tail(5))

# ---- T+8s ---- (consumer poll cycle = 5s)
time.sleep(6)
stamp("T+8s — consumer deve ter feito poll")
print("DB:", json.dumps(db_snapshot(), indent=2))
m = mission_snapshot()
print("MISSION:", json.dumps(m, indent=2) if m else "NOT FOUND")
print("LOG tail:", log_tail(10))

# ---- T+20s ----
time.sleep(12)
stamp("T+20s")
print("DB:", json.dumps(db_snapshot(), indent=2))
m = mission_snapshot()
print("MISSION status:", m['status'] if m else "NOT FOUND", "| progress:", m.get('progress') if m else "-")
print("LOG tail:", log_tail(15))

# ---- T+60s ----
time.sleep(40)
stamp("T+60s")
print("DB:", json.dumps(db_snapshot(), indent=2))
m = mission_snapshot()
if m:
    print("MISSION status:", m['status'])
    print("MISSION progress:", m.get('progress'))
    print("MISSION logs:", json.dumps(m.get('logs', []), indent=2))
    print("MISSION error:", m.get('error'))
    print("MISSION output:", str(m.get('metadata', {}).get('output', ''))[:500])
print("LOG tail:", log_tail(20))

# ---- T+120s ----
time.sleep(60)
stamp("T+120s — FINAL")
print("DB:", json.dumps(db_snapshot(), indent=2))
m = mission_snapshot()
if m:
    print("MISSION status:", m['status'])
    print("MISSION progress:", m.get('progress'))
    print("MISSION logs:", json.dumps(m.get('logs', []), indent=2))
    print("MISSION error:", m.get('error'))
    out = str(m.get('metadata', {}).get('output', ''))
    print("MISSION output (first 800 chars):", out[:800])
print("LOG tail:", log_tail(25))

# ---- events final ----
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute("SELECT COUNT(*) as cnt FROM events")
print("\nTOTAL EVENTS:", cur.fetchone()['cnt'])
conn.close()
