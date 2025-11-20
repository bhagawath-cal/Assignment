from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # PostgreSQL
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "movie_db"
    postgres_user: str = "postgres"
    postgres_password: str = ""
    
    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""
    
    # API
    api_host: str = "localhost"
    api_port: int = 8000
    
    # Optional: Deepseek API Key for LangGraph agent
    openai_api_key: str = ""
    tmdb_api_key: str = ""  # Optional: for fetching movie data from TMDB
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

