from dotenv import load_dotenv
import os
import logging
from typing import Dict

logger = logging.getLogger(__name__)

load_dotenv()

class Config:
    @staticmethod
    def get_env(key: str, default: str = None) -> str:
        return os.getenv(key, default)

    @staticmethod
    def parse_models(models_str: str) -> Dict:
        models_dict = {}
        if not models_str:
            return models_dict
            
        for model_str in models_str.split(';'):
            try:
                key, name, model_id, priority = model_str.split('|')
                models_dict[key] = {
                    'name': name,
                    'model': model_id,
                    'priority': int(priority)
                }
            except ValueError:
                logger.warning(f"Skipping invalid model config: {model_str}")
        return models_dict

# LLM Settings
DEFAULT_PROVIDER = Config.get_env("DEFAULT_LLM_PROVIDER", "ollama")
DEFAULT_TEMPERATURE = float(Config.get_env("DEFAULT_TEMPERATURE", "0.7"))

# OpenAI Config
OPENAI_API_KEY = Config.get_env("OPENAI_API_KEY")
OPENAI_DEFAULT_MODEL = Config.get_env("OPENAI_DEFAULT_MODEL", "gpt-4")
OPENAI_MODELS = Config.parse_models(Config.get_env("OPENAI_MODELS", ""))

# Ollama Config
OLLAMA_BASE_URL = Config.get_env("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_DEFAULT_MODEL = Config.get_env("OLLAMA_DEFAULT_MODEL", "llama3:8b-instruct-q8_0")
OLLAMA_MODELS = Config.parse_models(Config.get_env("OLLAMA_MODELS", ""))

# Database Config
MYSQL_USER = Config.get_env("MYSQL_USER")
MYSQL_PASSWORD = Config.get_env("MYSQL_PASSWORD")
MYSQL_HOST = Config.get_env("MYSQL_HOST")
MYSQL_DATABASE = Config.get_env("MYSQL_DATABASE")

# Get provider-specific default model
def get_default_model(provider: str) -> str:
    if provider == "openai":
        return OPENAI_DEFAULT_MODEL
    return OLLAMA_DEFAULT_MODEL

# Get available models for provider
def get_provider_models(provider: str) -> Dict:
    return OPENAI_MODELS if provider == "openai" else OLLAMA_MODELS