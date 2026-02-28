from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    # LLM
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    llm_provider: Literal["openai", "anthropic"] = "openai"
    llm_model: str = "gpt-4o"

    # Bright Data
    brightdata_api_token: str = ""

    # ActionBook
    actionbook_api_key: str = ""
    actionbook_base_url: str = "https://api.actionbook.dev"

    # Acontext
    acontext_api_key: str = ""

    # Database
    database_url: str = "sqlite+aiosqlite:///./agentforge.db"

    # App
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    frontend_url: str = "http://localhost:5173"

    # data.gov.sg
    datagov_base_url: str = "https://data.gov.sg/api/action/datastore_search"
    datagov_dataset_id: str = "d_8b84c4ee58e3cfc0ece0d773c8ca6abc"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
