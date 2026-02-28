import os
from acontext import AcontextClient
from dotenv import load_dotenv

load_dotenv()

client = AcontextClient(api_key=os.getenv("ACONTEXT_API_KEY"))

def create_session(user_query: str) -> str:
    session = client.sessions.create(user="hdb-agent")
    # Store the initial query
    client.sessions.store_message(
        session.id,
        blob={"role": "user", "content": user_query}
    )
    print(f"📝 Session created: {session.id}")
    return session.id

def save_to_session(session_id: str, key: str, value):
    client.sessions.store_message(
        session_id,
        blob={"role": "assistant", "content": f"{key}: {str(value)[:500]}"}
    )

def get_from_session(session_id: str, key: str):
    messages = client.sessions.get_messages(session_id=session_id)
    for msg in reversed(messages.items):
        if msg.get("blob", {}).get("content", "").startswith(f"{key}:"):
            return msg["blob"]["content"]
    return None
