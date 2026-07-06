from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "FinGuard AI"
    environment: str = "development"

    database_url: str
    redis_url: str

    openai_api_key: str
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-4o-mini"

    chroma_collection_name: str = "finguard_transactions"
    chroma_persist_path: str = "./chroma_data"

    class Config:
        env_file = ".env"


settings = Settings()
