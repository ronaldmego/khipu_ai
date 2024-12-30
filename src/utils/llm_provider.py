from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_ollama import OllamaLLM
from langchain_core.language_models.chat_models import BaseChatModel
import streamlit as st
import logging
import requests
from config.config import (
    OPENAI_MODELS, OLLAMA_MODELS, get_default_model,
    OLLAMA_BASE_URL, get_provider_models
)

logger = logging.getLogger(__name__)

class LLMProvider:
    @staticmethod
    def get_llm(provider: str = "openai", model_name: Optional[str] = None, **kwargs) -> BaseChatModel:
        try:
            if provider == "openai":
                api_key = st.session_state.get('OPENAI_API_KEY')
                if not api_key:
                    raise ValueError("OpenAI API key not found in session state")
                
                model_info = OPENAI_MODELS.get(model_name or get_default_model("openai"))
                if not model_info:
                    raise ValueError(f"Model {model_name} not found in configuration")
                
                return ChatOpenAI(
                    model=model_info['model'],
                    temperature=kwargs.get('temperature', 0.7),
                    openai_api_key=api_key
                )
            
            elif provider == "ollama":
                return OllamaLLM(
                    model=model_name or get_default_model("ollama"),
                    temperature=kwargs.get('temperature', 0.7),
                    base_url=OLLAMA_BASE_URL
                )
            
            else:
                raise ValueError(f"Unsupported LLM provider: {provider}")
                
        except Exception as e:
            logger.error(f"Error initializing LLM provider: {str(e)}")
            raise

    @staticmethod
    def check_ollama_availability() -> bool:
        try:
            response = requests.get(f"{OLLAMA_BASE_URL}/api/version", timeout=2)
            if response.status_code == 200:
                models_response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
                if models_response.status_code == 200:
                    return True
            return False
        except:
            return False

    @staticmethod
    def list_available_models(provider: str) -> list:
        if provider == "openai":
            models = get_provider_models("openai")
            return sorted(models.keys(), key=lambda x: models[x]['priority'])
        elif provider == "ollama":
            try:
                response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
                if response.status_code == 200:
                    models = response.json().get('models', [])
                    return [model['name'] for model in models]
            except:
                pass
            return [get_default_model("ollama")]
        return []

    @staticmethod
    def get_model_display_name(model_name: str, provider: str = "openai") -> str:
        if provider == "openai":
            models = get_provider_models("openai")
            if model_info := models.get(model_name):
                return model_info['name']
        return model_name