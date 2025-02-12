from pydantic import Field
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
from src.assistant.logger import logger
from datetime import datetime
from langsmith import traceable
import os, pytz


class Settings(BaseSettings):
    """LangSmith"""
    LANGCHAIN_TRACING_V2: str = Field("true", env="LANGCHAIN_TRACING_V2")
    LANGCHAIN_API_KEY: str = Field("",
        env="LANGCHAIN_API_KEY")
    LANGCHAIN_PROJECT: str = Field("Research", env="LANGCHAIN_PROJECT")
    
    """TAVILY"""
    TAVILY_API_KEY: str = Field("", env="TAVILY_API_KEY")

    """LLM"""
    OLLAMA_BASE_URL: Optional[str] = Field("",
                                          env="OLLAMA_BASE_URL")
    
    class Config:
        env_file = ".env"


class Config(Settings):

    def __init__(self):
        super().__init__()
        self.setup_environment()

    def setup_environment(self):
        os.environ["LANGCHAIN_TRACING_V2"] = Settings(
        ).LANGCHAIN_TRACING_V2
        os.environ["LANGCHAIN_API_KEY"] = Settings().LANGCHAIN_API_KEY
        os.environ["LANGCHAIN_PROJECT"] = Settings().LANGCHAIN_PROJECT
        os.environ["TAVILY_API_KEY"] = Settings().TAVILY_API_KEY
        os.environ["OLLAMA_BASE_URL"] = Settings().OLLAMA_BASE_URL


@lru_cache()
def get_configs():
    configs = Config()
    config_vars = vars(configs)
    for key, value in config_vars.items():
        if key.isupper() and key not in (
                "TAVILY_API_KEY", "OLLAMA_BASE_URL", "LANGCHAIN_API_KEY") and value is not None:
            if 'KEY' not in key:
                logger.debug(f"{key} ok ... : {value}")

    return configs


configs = get_configs()
