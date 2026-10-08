"""
FASE 43.6 — FORCE COGNITION LOOP — Observation Script
=====================================================
This script:
1. Starts the REAL CognitionLoop in a background thread
2. Creates a mission via mission_engine directly
3. Approves it via SafeActionQueue
4. Observes for 180 seconds, logging all transitions
5. Produces final report

Must run from DGM-MAT root with the runtime NOT already running
(this script bootstraps the minimum needed).
"""

import sys
import os
import time
import json
import asyncio
import threading
import traceback
from datetime import datetime
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# ─── Minimal bootstrap ───────────────────────────────────────────────
print(f"[{datetime.now().isoformat()}] FASE 43.6: Initializing...")

from core.observability.logger import dgm_logger
from core.autonomy.mission_engine import mission_engine, MissionStatus
from core.runtime.safe_action_queue import SafeActionQueue

# Observation log
observations = []

def log_obs(tag, data=None):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "tag": tag,
        "data": data or {}
    }
    observations.append(entry)
    print(f"  [{entry['timestamp']}] {tag}: {json.dumps(data or {}, default=str)[:200]}")


# ─── STEP 1: Start CognitionLoop in background thread ────────────────
log_obs("STEP_1_START", {"action": "Starting CognitionLoop in background thread"})

cognition_loop_instance = None
cognition_thread = None
cognition_error = None

def run_cognition_loop():
    global cognition_loop_instance, cognition_error
    try:
        from core.autonomy.active_runtime.cognition_loop import CognitionLoop
        cognition_loop_instance = CognitionLoop()
        log_obs("COGNITION_LOOP_CREATED", {
            "class": "CognitionLoop",
            "config": cognition_loop_instance.config,
            "running": cognition_loop_instance.running
        })

        # Run the async loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(cognition_loop_instance.start())
    except Exception as e:
        cognition_error = str(e)
        log_obs("COGNITION_LOOP_ERROR", {
            "error": str(e),
            "traceback": traceback.format_exc()
        })

cognition_thread = threading.Thread(target=run_cognition_loop, daemon=True, name="ForcedCognitionLoop")
cognition_thread.start()
log_obs("COGNITION_THREAD_STARTED", {"thread_name": cognition_thread.name, "alive": cognition_thread.is_alive()})

# Give it time to initialize
time.sleep(3)

log_obs("STEP_1_RESULT", {
    "thread_alive": cognition_thread.is_alive(),
    "loop_instance_exists": cognition_loop_instance is not None,
    "loop_running": cognition_loop_instance.running if cognition_loop_instance else False,
    "cognition_error": cognition_error
})


# ─── STEP 2: Create mission ──────────────────────────────────────────
log_obs("STEP_2_START", {"action": "Creating test mission"})

try:
    mission = mission_engine.create_mission(
        goal="phase 43.6 cognition test",
        description="FASE 43.6 forced cognition loop validation"
    )
    mission_id = mission.mission_id
    log_obs("MISSION_CREATED", {
        "mission_id": mission_id,
        "goal": mission.goal,
        "status": mission.status.value,
        "metadata": {k: v for k, v in mission.metadata.items() if k != "result"},
        "logs": mission.logs
    })
except Exception as e:
    log_obs("MISSION_CREATE_FAILED", {"error": str(e), "traceback": traceback.format_exc()})
    mission_id = None


# ─── STEP 3: Approve manually ────────────────────────────────────────
if mission_id:
    log_obs("STEP_3_START", {"action": "Approving mission in SafeActionQueue"})
    time.sleep(2)  # Let queue settle

    try:
        queue = SafeActionQueue()
        action_id = mission.metadata.get("action_id")

        if action_id:
            log_obs("QUEUE_ACTION_FOUND", {"action_id": action_id})
            # Check current status
            action_info = queue.get_action(action_id)
            log_obs("QUEUE_ACTION_STATUS_BEFORE", action_info or {"error": "action not found"})

            # Approve
            queue.approve(action_id, operator="fase_43_6_test")
            time.sleep(1)
            action_info_after = queue.get_action(action_id)
            log_obs("QUEUE_ACTION_STATUS_AFTER_APPROVE", action_info_after or {"error": "action not found"})
        else:
            log_obs("QUEUE_NO_ACTION_ID", {"metadata": mission.metadata})
    except Exception as e:
        log_obs("APPROVAL_FAILED", {"error": str(e), "traceback": traceback.format_exc()})


# ─── STEP 4: Observe 180 seconds ─────────────────────────────────────
log_obs("STEP_4_START", {"action": "Observing for 180 seconds", "start_time": datetime.now().isoformat()})

process_missions_calls = 0
observation_start = time.monotonic()
OBSERVATION_DURATION = 180
check_interval = 5  # Check every 5 seconds

last_status = None
status_transitions = []

cpu_samples = []

try:
    import psutil
    has_psutil = True
except ImportError:
    has_psutil = False

while (time.monotonic() - observation_start) < OBSERVATION_DURATION:
    elapsed = round(time.monotonic() - observation_start, 1)

    # Check mission status
    if mission_id and mission_id in mission_engine.active_missions:
        m = mission_engine.active_missions[mission_id]
        current_status = m.status.value

        if current_status != last_status:
            transition = {
                "from": last_status,
                "to": current_status,
                "at_seconds": elapsed,
                "progress": m.progress,
                "logs_count": len(m.logs),
                "last_log": m.logs[-1] if m.logs else None,
                "subtasks": len(m.subtasks) if m.subtasks else 0,
                "error": m.error
            }
            status_transitions.append(transition)
            log_obs("MISSION_TRANSITION", transition)
            last_status = current_status

        # Check subtask states
        if m.subtasks:
            subtask_states = [{"id": st.subtask_id, "title": st.title, "status": st.status} for st in m.subtasks]
            if elapsed % 30 < check_interval:  # Log subtasks every ~30s
                log_obs("SUBTASK_STATES", {"elapsed": elapsed, "subtasks": subtask_states})

    # Check cognition loop state
    if cognition_loop_instance:
        if elapsed % 30 < check_interval:  # Log loop state every ~30s
            log_obs("COGNITION_LOOP_STATE", {
                "elapsed": elapsed,
                "running": cognition_loop_instance.running,
                "cycle_count": cognition_loop_instance.cycle_count,
                "thread_alive": cognition_thread.is_alive()
            })

    # Check queue state
    if elapsed % 30 < check_interval:
        try:
            q = SafeActionQueue()
            health = q.get_health()
            log_obs("QUEUE_HEALTH", {"elapsed": elapsed, "health": health})
        except Exception:
            pass

    # CPU sample
    if has_psutil and elapsed % 15 < check_interval:
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory().percent
        cpu_samples.append({"elapsed": elapsed, "cpu": cpu, "memory": mem})

    # Check if mission already completed — continue observing but note it
    if mission_id and mission_id in mission_engine.active_missions:
        m = mission_engine.active_missions[mission_id]
        if m.status in (MissionStatus.COMPLETED, MissionStatus.FAILED):
            if elapsed > 30:  # Observe at least 30s after completion
                log_obs("EARLY_EXIT", {"reason": "Mission terminal state reached", "elapsed": elapsed})
                break

    time.sleep(check_interval)

observation_end = time.monotonic()
total_observation = round(observation_end - observation_start, 1)

# ─── STEP 5: Final Report ────────────────────────────────────────────
log_obs("STEP_5_START", {"action": "Generating final report"})

# Final mission state
final_mission = None
if mission_id and mission_id in mission_engine.active_missions:
    m = mission_engine.active_missions[mission_id]
    final_mission = {
        "mission_id": m.mission_id,
        "goal": m.goal,
        "status": m.status.value,
        "progress": m.progress,
        "logs": m.logs,
        "error": m.error,
        "subtasks": [{"id": st.subtask_id, "title": st.title, "status": st.status} for st in m.subtasks] if m.subtasks else [],
        "metadata_keys": list(m.metadata.keys()),
        "has_result": "result" in m.metadata,
        "has_output": "output" in m.metadata
    }

# Final queue state
final_queue = None
try:
    q = SafeActionQueue()
    if action_id:
        final_queue = q.get_action(action_id)
except Exception:
    pass

# Cognition loop final state
final_cognition = {
    "instance_exists": cognition_loop_instance is not None,
    "running": cognition_loop_instance.running if cognition_loop_instance else False,
    "cycle_count": cognition_loop_instance.cycle_count if cognition_loop_instance else 0,
    "thread_alive": cognition_thread.is_alive() if cognition_thread else False,
    "error": cognition_error
}

report = {
    "fase": "43.6",
    "total_observation_seconds": total_observation,
    "answers": {
        "1_cognition_loop_started": cognition_loop_instance is not None and cognition_loop_instance.running,
        "2_process_missions_called_periodically": cognition_loop_instance.cycle_count > 0 if cognition_loop_instance else False,
        "3_subtasks_changed_state": False,
        "4_mission_left_running": False,
        "5_mission_completed": False,
        "6_new_blockage": None
    },
    "status_transitions": status_transitions,
    "final_mission": final_mission,
    "final_queue": final_queue,
    "final_cognition": final_cognition,
    "cpu_samples": cpu_samples,
    "cognition_cycle_count": cognition_loop_instance.cycle_count if cognition_loop_instance else 0,
    "observation_count": len(observations)
}

# Fill in answers from observed data
if final_mission:
    report["answers"]["5_mission_completed"] = final_mission["status"] == "completed"
    report["answers"]["4_mission_left_running"] = final_mission["status"] != "running" or any(
        t["to"] != "running" for t in status_transitions if t["from"] == "running"
    )
    if final_mission["subtasks"]:
        report["answers"]["3_subtasks_changed_state"] = any(
            st["status"] != "pending" for st in final_mission["subtasks"]
        )

# Detect new blockage
if cognition_error:
    report["answers"]["6_new_blockage"] = f"CognitionLoop error: {cognition_error}"
elif final_mission and final_mission["status"] not in ("completed", "failed"):
    report["answers"]["6_new_blockage"] = f"Mission stuck in {final_mission['status']}"
elif final_mission and final_mission["error"]:
    report["answers"]["6_new_blockage"] = f"Mission failed with: {final_mission['error']}"
else:
    report["answers"]["6_new_blockage"] = "None detected"


print("\n" + "=" * 80)
print("FASE 43.6 — FINAL REPORT")
print("=" * 80)
print(json.dumps(report, indent=2, default=str))

# Save report
report_path = Path(__file__).resolve().parent / "fase_43_6_report.json"
with open(report_path, "w") as f:
    json.dump(report, f, indent=2, default=str)
print(f"\nReport saved to: {report_path}")

# Save full observation log
obs_path = Path(__file__).resolve().parent / "fase_43_6_observations.json"
with open(obs_path, "w") as f:
    json.dump(observations, f, indent=2, default=str)
print(f"Observations saved to: {obs_path}")

# Stop cognition loop
if cognition_loop_instance:
    cognition_loop_instance.stop()
    log_obs("COGNITION_LOOP_STOPPED", {})

print("\nFASE 43.6 complete.")
