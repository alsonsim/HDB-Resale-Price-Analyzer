import json, os, uuid
from datetime import datetime

SESSION_FILE = "./data/sessions.json"

def _load():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE) as f:
            return json.load(f)
    return {}

def _save(data):
    os.makedirs("./data", exist_ok=True)
    with open(SESSION_FILE, "w") as f:
        json.dump(data, f, indent=2)

def create_session(user_query: str) -> str:
    sessions = _load()
    session_id = str(uuid.uuid4())[:8]
    sessions[session_id] = {
        "query": user_query,
        "created_at": datetime.now().isoformat(),
        "data": {}
    }
    _save(sessions)
    print(f"📝 Session created: {session_id}")
    return session_id

def save_to_session(session_id: str, key: str, value):
    sessions = _load()
    sessions[session_id]["data"][key] = value
    _save(sessions)

def get_from_session(session_id: str, key: str):
    sessions = _load()
    return sessions.get(session_id, {}).get("data", {}).get(key)
