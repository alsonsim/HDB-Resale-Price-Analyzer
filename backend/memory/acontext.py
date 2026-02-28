from backend.config import settings


class AcontextMemoryManager:
    """Wrapper for Acontext — context management for AI agent workflows.

    Acontext provides three memory layers:
    - Short-term: conversation messages within a session
    - Mid-term: task state tracking and session summaries
    - Long-term: learned skills distilled from past agent interactions

    When no API key is configured, falls back to in-memory storage.
    """

    def __init__(self):
        self.api_key = settings.acontext_api_key
        self._client = None
        # In-memory fallback for development
        self._local_sessions: dict[str, list[dict]] = {}
        self._local_skills: list[dict] = []

    def _get_client(self):
        if self._client is None and self.api_key:
            try:
                from acontext import AcontextClient
                self._client = AcontextClient(api_key=self.api_key)
            except ImportError:
                self._client = None
        return self._client

    async def store_message(self, session_id: str, role: str, content: str):
        """Store a conversation message in session memory."""
        client = self._get_client()

        if client:
            try:
                client.store_message(
                    session_id=session_id,
                    message={"role": role, "content": content},
                )
                return
            except Exception:
                pass

        # Fallback: in-memory
        if session_id not in self._local_sessions:
            self._local_sessions[session_id] = []
        self._local_sessions[session_id].append({"role": role, "content": content})

        # Keep last 50 messages per session
        if len(self._local_sessions[session_id]) > 50:
            self._local_sessions[session_id] = self._local_sessions[session_id][-50:]

    async def get_session_context(self, session_id: str) -> list[dict]:
        """Retrieve conversation history for a session."""
        client = self._get_client()

        if client:
            try:
                messages = client.get_messages(session_id=session_id)
                return messages if messages else []
            except Exception:
                pass

        # Fallback: in-memory
        return self._local_sessions.get(session_id, [])

    async def get_session_summary(self, session_id: str) -> str | None:
        """Get an AI-generated summary of the session so far."""
        client = self._get_client()

        if client:
            try:
                summary = client.get_session_summary(session_id=session_id)
                return summary
            except Exception:
                pass

        # Fallback: summarize from local history
        messages = self._local_sessions.get(session_id, [])
        if not messages:
            return None
        return f"Session with {len(messages)} messages about HDB resale market."

    async def store_skill(self, name: str, description: str, parameters: dict):
        """Store a reusable skill/capability learned from agent interactions."""
        client = self._get_client()

        skill = {
            "name": name,
            "description": description,
            "parameters": parameters,
        }

        if client:
            try:
                client.store_skill(skill)
                return
            except Exception:
                pass

        # Fallback
        self._local_skills.append(skill)

    async def list_skills(self) -> list[dict]:
        """List all stored agent skills."""
        client = self._get_client()

        if client:
            try:
                return client.list_skills()
            except Exception:
                pass

        return self._local_skills

    async def clear_session(self, session_id: str):
        """Clear all messages for a session."""
        client = self._get_client()

        if client:
            try:
                client.flush(session_id=session_id)
                return
            except Exception:
                pass

        self._local_sessions.pop(session_id, None)


memory_manager = AcontextMemoryManager()
