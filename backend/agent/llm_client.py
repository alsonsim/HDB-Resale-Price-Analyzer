from backend.config import settings


class LLMClient:
    """Unified interface for Claude and GPT models."""

    def __init__(self):
        self.provider = settings.llm_provider
        self.model = settings.llm_model
        self._openai_client = None
        self._anthropic_client = None

    def _get_openai(self):
        if self._openai_client is None:
            from openai import AsyncOpenAI
            self._openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
        return self._openai_client

    def _get_anthropic(self):
        if self._anthropic_client is None:
            from anthropic import AsyncAnthropic
            self._anthropic_client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        return self._anthropic_client

    async def generate(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ) -> str:
        """Generate a response from the configured LLM."""
        if self.provider == "anthropic":
            return await self._generate_anthropic(
                system_prompt, user_message, temperature, max_tokens
            )
        return await self._generate_openai(
            system_prompt, user_message, temperature, max_tokens
        )

    async def _generate_openai(
        self, system_prompt: str, user_message: str, temperature: float, max_tokens: int
    ) -> str:
        client = self._get_openai()
        response = await client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""

    async def _generate_anthropic(
        self, system_prompt: str, user_message: str, temperature: float, max_tokens: int
    ) -> str:
        client = self._get_anthropic()
        response = await client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
            temperature=temperature,
        )
        return response.content[0].text


llm_client = LLMClient()
