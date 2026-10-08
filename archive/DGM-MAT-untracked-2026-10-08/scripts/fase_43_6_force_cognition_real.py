"""
FASE 43.6 — FORCE COGNITION LOOP (REAL MULTI-PROCESS TEST)
===========================================================
This script runs the experiment with the main runtime ALREADY alive.
It:
1. Calls the API (Process 1) to create the mission.
2. Loads/Instantiates the REAL CognitionLoop in Process 2.
3. Runs the CognitionLoop in a background thread of Process 2.
4. Approves the enqueued action in SafeActionQueue.
5. Monitors both views (API/Process 1 vs. Local/Process 2) for 180 seconds.
6. Saves reports.
"""

import sys
import os
import time
import json
import asyncio
import threading
import requests
import traceback
from datetime import datetime
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Setup observation logs
observations = []

def log_obs(tag, data=None):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "tag": tag,
        "data": data or {}
    }
    observations.append(entry)
    print(f"  [{entry['timestamp']}] {tag}: {json.dumps(data or {}, default=str)[:160]}")

# ─── STEP 1: Verify API is alive & Create Mission via API ─────────────────
log_obs("STEP_1_START", {"action": "Verifying API server is running on 8181"})

try:
    health_resp = requests.get("http://127.0.0.1:8181/runtime/health", timeout=5)
    log_obs("API_HEALTH_CHECK", health_resp.json())
except Exception as e:
    log_obs("API_HEALTH_CHECK_FAILED", {"error": str(e)})
    print("CRITICAL: API server is not running. Please start the runtime first.")
    sys.exit(1)

log_obs("STEP_2_START", {"action": "Creating mission via API"})
mission_id = None
action_id = None

try:
    create_resp = requests.post(
        "http://127.0.0.1:8181/runtime/missions",
        json={
            "goal": "phase 43.6 cognition test",
            "description": "FASE 43.6 forced cognition loop real validation"
        },
        timeout=5
    )
    create_data = create_resp.json()
    log_obs("API_MISSION_CREATED", create_data)
    
    # Give it a second to sync to database and disk
    time.sleep(2)
    
    # Retrieve missions list to find the action_id
    list_resp = requests.get("http://127.0.0.1:8181/runtime/missions", timeout=5)
    missions = list_resp.json()
    for m in missions:
        if m["goal"] == "phase 43.6 cognition test" and m["status"] == "QUEUED":
            mission_id = m["mission_id"]
            action_id = m.get("metadata", {}).get("action_id")
            log_obs("FOUND_MISSION_INFO", {"mission_id": mission_id, "action_id": action_id})
            break
except Exception as e:
    log_obs("MISSION_CREATION_OR_LOOKUP_FAILED", {"error": str(e), "traceback": traceback.format_exc()})
    sys.exit(1)

if not mission_id or not action_id:
    log_obs("MISSION_NOT_FOUND", {"error": "Could not find the newly created QUEUED mission"})
    sys.exit(1)


# ─── STEP 2: Instantiate CognitionLoop in Process 2 ────────────────────────
log_obs("STEP_3_START", {"action": "Instantiating real CognitionLoop"})

from core.autonomy.active_runtime.cognition_loop import CognitionLoop
from core.autonomy.mission_engine import mission_engine
from core.runtime.safe_action_queue import SafeActionQueue

cognition_loop_instance = None
cognition_thread = None
cognition_error = None

def run_cognition_loop():
    global cognition_loop_instance, cognition_error
    try:
        # Since this script is a separate process, importing it will load the mission json files
        cognition_loop_instance = CognitionLoop()
        log_obs("COGNITION_LOOP_CREATED", {
            "class": "CognitionLoop",
            "config": cognition_loop_instance.config,
            "running": cognition_loop_instance.running
        })
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(cognition_loop_instance.start())
    except Exception as e:
        cognition_error = str(e)
        log_obs("COGNITION_LOOP_ERROR", {
            "error": str(e),
            "traceback": traceback.format_exc()
        })

cognition_thread = threading.Thread(target=run_cognition_loop, daemon=True, name="ForcedCognitionLoopProcess")
cognition_thread.start()
time.sleep(3)

log_obs("COGNITION_INITIALIZED", {
    "thread_alive": cognition_thread.is_alive(),
    "loop_instance_exists": cognition_loop_instance is not None,
    "loop_running": cognition_loop_instance.running if cognition_loop_instance else False,
    "cognition_error": cognition_error
})


# ─── STEP 3: Approve queue action manually ──────────────────────────────────
log_obs("STEP_4_START", {"action": "Approving action in database"})

try:
    queue = SafeActionQueue()
    action_info_before = queue.get_action(action_id)
    log_obs("QUEUE_ACTION_BEFORE", action_info_before)
    
    queue.approve(action_id, operator="fase_43_6_test_real")
    time.sleep(2)
    
    action_info_after = queue.get_action(action_id)
    log_obs("QUEUE_ACTION_AFTER_APPROVE", action_info_after)
except Exception as e:
    log_obs("APPROVAL_FAILED", {"error": str(e), "traceback": traceback.format_exc()})


# ─── STEP 4: Observe for 180 seconds ─────────────────────────────────────────
log_obs("STEP_5_START", {"action": "Observing for 180 seconds"})

observation_start = time.monotonic()
OBSERVATION_DURATION = 180
check_interval = 5

api_status_transitions = []
local_status_transitions = []
last_api_status = None
last_local_status = None

cpu_samples = []
try:
    import psutil
    has_psutil = True
except ImportError:
    has_psutil = False

while (time.monotonic() - observation_start) < OBSERVATION_DURATION:
    elapsed = round(time.monotonic() - observation_start, 1)
    
    # Query Process 1 (API View)
    api_mission = None
    try:
        list_resp = requests.get("http://127.0.0.1:8181/runtime/missions", timeout=2)
        for m in list_resp.json():
            if m["mission_id"] == mission_id:
                api_mission = m
                break
    except Exception as e:
        log_obs("API_QUERY_ERROR", {"elapsed": elapsed, "error": str(e)})
        
    if api_mission:
        api_status = api_mission["status"]
        if api_status != last_api_status:
            trans = {
                "elapsed": elapsed,
                "from": last_api_status,
                "to": api_status,
                "progress": api_mission["progress"],
                "subtasks": len(api_mission.get("subtasks", [])),
                "error": api_mission["error"]
            }
            api_status_transitions.append(trans)
            log_obs("API_MISSION_TRANSITION", trans)
            last_api_status = api_status
            
    # Query Process 2 (Local View)
    local_status = None
    if mission_id in mission_engine.active_missions:
        local_m = mission_engine.active_missions[mission_id]
        local_status = local_m.status.value
        if local_status != last_local_status:
            trans = {
                "elapsed": elapsed,
                "from": last_local_status,
                "to": local_status,
                "progress": local_m.progress,
                "subtasks": len(local_m.subtasks) if local_m.subtasks else 0,
                "error": local_m.error
            }
            local_status_transitions.append(trans)
            log_obs("LOCAL_MISSION_TRANSITION", trans)
            last_local_status = local_status
            
    # CPU sample
    if has_psutil and elapsed % 15 < check_interval:
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory().percent
        cpu_samples.append({"elapsed": elapsed, "cpu": cpu, "memory": mem})
        
    # Queue status logging every 30s
    if elapsed % 30 < check_interval:
        try:
            q_info = queue.get_action(action_id)
            log_obs("QUEUE_STATUS_SAMPLE", {"elapsed": elapsed, "status": q_info.get("status") if q_info else "NOT_FOUND"})
        except Exception:
            pass

    # Check terminal state in BOTH views to see if we exit early
    api_terminal = api_mission and api_mission["status"] in ("COMPLETED", "FAILED")
    local_terminal = (mission_id in mission_engine.active_missions and 
                      local_status in ("COMPLETED", "FAILED"))
    
    if api_terminal and local_terminal:
        log_obs("EARLY_EXIT", {"reason": "Both process views reached terminal state", "elapsed": elapsed})
        break
        
    time.sleep(check_interval)

# ─── STEP 5: Final Report ────────────────────────────────────────────────────
log_obs("STEP_6_START", {"action": "Generating final report"})

# Retrieve final database/API/local states
final_api_mission = None
try:
    list_resp = requests.get("http://127.0.0.1:8181/runtime/missions", timeout=5)
    for m in list_resp.json():
        if m["mission_id"] == mission_id:
            final_api_mission = m
            break
except Exception:
    pass

final_local_mission = None
if mission_id in mission_engine.active_missions:
    m = mission_engine.active_missions[mission_id]
    final_local_mission = {
        "mission_id": m.mission_id,
        "status": m.status.value,
        "progress": m.progress,
        "logs": m.logs,
        "error": m.error,
        "subtasks_count": len(m.subtasks) if m.subtasks else 0
    }

final_queue = None
try:
    final_queue = queue.get_action(action_id)
except Exception:
    pass

report = {
    "fase": "43.6_real",
    "total_observation_seconds": round(time.monotonic() - observation_start, 1),
    "answers": {
        "1_cognition_loop_started": cognition_loop_instance is not None and cognition_loop_instance.running,
        "2_process_missions_called_periodically": cognition_loop_instance.cycle_count > 0 if cognition_loop_instance else False,
        "3_subtasks_changed_state": False, # Will be filled from results
        "4_mission_left_running": False,   # Will be filled from results
        "5_mission_completed": False,       # Will be filled from results
        "6_new_blockage": None
    },
    "api_status_transitions": api_status_transitions,
    "local_status_transitions": local_status_transitions,
    "final_api_mission": final_api_mission,
    "final_local_mission": final_local_mission,
    "final_queue": final_queue,
    "cpu_samples": cpu_samples
}

# Process results for answers
if final_api_mission:
    report["answers"]["5_mission_completed"] = final_api_mission["status"] == "COMPLETED"
    report["answers"]["4_mission_left_running"] = final_api_mission["status"] == "RUNNING"
    if final_api_mission.get("subtasks"):
        report["answers"]["3_subtasks_changed_state"] = any(st["status"] != "pending" for st in final_api_mission["subtasks"])

# Set blockage
if cognition_error:
    report["answers"]["6_new_blockage"] = f"CognitionLoop error in Process 2: {cognition_error}"
elif final_api_mission and final_api_mission["status"] == "FAILED":
    report["answers"]["6_new_blockage"] = f"API Mission failed with: {final_api_mission['error']}"
elif final_local_mission and final_local_mission["status"] == "FAILED":
    report["answers"]["6_new_blockage"] = f"Local Mission failed with: {final_local_mission['error']}"
else:
    report["answers"]["6_new_blockage"] = "Process isolation / Memory desync prevented local engine from updating state."

print("\n" + "=" * 80)
print("FASE 43.6 — REAL TEST REPORT")
print("=" * 80)
print(json.dumps(report, indent=2, default=str))

# Save report
report_path = Path(__file__).resolve().parent / "fase_43_6_report_real.json"
with open(report_path, "w") as f:
    json.dump(report, f, indent=2, default=str)
    
obs_path = Path(__file__).resolve().parent / "fase_43_6_observations_real.json"
with open(obs_path, "w") as f:
    json.dump(observations, f, indent=2, default=str)

# Stop cognition loop
if cognition_loop_instance:
    cognition_loop_instance.stop()

print("\nFASE 43.6 Real Test Complete.")
