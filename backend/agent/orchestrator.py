import uuid

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.agent.llm_client import llm_client
from backend.agent.prompts import SYSTEM_PROMPT, CHAT_PROMPT
from backend.models.database import ResaleTransaction
from backend.models.schemas import ChatResponse
from backend.memory.acontext import memory_manager


class AgentOrchestrator:
    """Main agent loop: query → context retrieval → LLM → response.

    Flow:
    1. Receive user query
    2. Load session context from Acontext
    3. Retrieve relevant data from DB
    4. If needed, trigger scraping via Bright Data / ActionBook
    5. Generate AI response
    6. Store session context back to Acontext
    7. Return response
    """

    async def handle_query(
        self,
        message: str,
        session_id: str | None,
        db: AsyncSession,
    ) -> ChatResponse:
        # Create or resume session
        if not session_id:
            session_id = str(uuid.uuid4())

        # Load conversation history from Acontext
        history = await memory_manager.get_session_context(session_id)

        # Retrieve relevant data based on the query
        context_data = await self._build_context(message, db)

        # Store user message
        await memory_manager.store_message(session_id, "user", message)

        # Build the prompt with context
        context_str = self._format_context(context_data, history)
        prompt = CHAT_PROMPT.format(context=context_str)

        # Generate AI response
        reply = await llm_client.generate(
            system_prompt=SYSTEM_PROMPT,
            user_message=f"{prompt}\n\nUser: {message}",
        )

        # Store assistant response
        await memory_manager.store_message(session_id, "assistant", reply)

        return ChatResponse(
            reply=reply,
            session_id=session_id,
            data=context_data if context_data else None,
        )

    async def _build_context(self, message: str, db: AsyncSession) -> dict | None:
        """Extract relevant data from DB based on the user's message."""
        from backend.utils.helpers import HDB_TOWNS, HDB_FLAT_TYPES

        message_upper = message.upper()

        # Detect town mentions
        detected_town = None
        for town in HDB_TOWNS:
            if town in message_upper:
                detected_town = town
                break

        # Detect flat type mentions
        detected_flat_type = None
        for ft in HDB_FLAT_TYPES:
            if ft in message_upper:
                detected_flat_type = ft
                break
        # Also check shorthand like "4-room" or "4 room"
        if not detected_flat_type:
            for n in ["1", "2", "3", "4", "5"]:
                if f"{n}-ROOM" in message_upper or f"{n} ROOM" in message_upper:
                    detected_flat_type = f"{n} ROOM"
                    break

        if not detected_town:
            return None

        # Query recent transactions for the detected town
        conditions = [ResaleTransaction.town == detected_town]
        if detected_flat_type:
            conditions.append(ResaleTransaction.flat_type == detected_flat_type)

        query = (
            select(ResaleTransaction)
            .where(and_(*conditions))
            .order_by(ResaleTransaction.month.desc())
            .limit(20)
        )
        result = await db.execute(query)
        transactions = result.scalars().all()

        if not transactions:
            return {"town": detected_town, "flat_type": detected_flat_type, "transactions": []}

        prices = [t.resale_price for t in transactions]
        areas = [t.floor_area_sqm for t in transactions if t.floor_area_sqm]

        return {
            "town": detected_town,
            "flat_type": detected_flat_type,
            "transaction_count": len(transactions),
            "avg_price": round(sum(prices) / len(prices), 2),
            "min_price": min(prices),
            "max_price": max(prices),
            "avg_area": round(sum(areas) / len(areas), 2) if areas else None,
            "period": f"{transactions[-1].month} to {transactions[0].month}",
            "recent_transactions": [
                {
                    "month": t.month,
                    "block": t.block,
                    "street_name": t.street_name,
                    "storey_range": t.storey_range,
                    "floor_area_sqm": t.floor_area_sqm,
                    "resale_price": t.resale_price,
                    "flat_model": t.flat_model,
                    "remaining_lease": t.remaining_lease,
                }
                for t in transactions[:10]
            ],
        }

    def _format_context(self, data: dict | None, history: list[dict]) -> str:
        parts = []

        if history:
            parts.append("**Previous conversation:**")
            for msg in history[-6:]:  # Last 3 exchanges
                role = msg.get("role", "user")
                content = msg.get("content", "")
                parts.append(f"  {role}: {content[:200]}")

        if data:
            parts.append(f"\n**Data for {data.get('town', 'N/A')}:**")
            if data.get("flat_type"):
                parts.append(f"  Flat type: {data['flat_type']}")
            parts.append(f"  Transactions found: {data.get('transaction_count', 0)}")
            if data.get("avg_price"):
                parts.append(f"  Average price: ${data['avg_price']:,.0f}")
                parts.append(f"  Range: ${data['min_price']:,.0f} - ${data['max_price']:,.0f}")
                parts.append(f"  Period: {data.get('period', 'N/A')}")

            if data.get("recent_transactions"):
                parts.append("\n  **Recent comparable transactions:**")
                for t in data["recent_transactions"][:5]:
                    parts.append(
                        f"  - {t['month']} | {t['block']} {t['street_name']} | "
                        f"{t['storey_range']} | {t['floor_area_sqm']}sqm | "
                        f"${t['resale_price']:,.0f} | {t['remaining_lease']}"
                    )

        return "\n".join(parts) if parts else "No specific data context available."


agent_orchestrator = AgentOrchestrator()
