"""
Singleton service for shared Memory and PostgresStorage instances.
"""
import threading
from agno.memory.v2.db.postgres import PostgresMemoryDb
from agno.memory.v2.memory import Memory
from agno.storage.postgres import PostgresStorage
from .config import DEFAULT_MODEL_TYPE, DEFAULT_MODEL_ID, POSTGRES_CONNECTION
from agno.models.groq import Groq
from agno.models.google import Gemini
from agno.models.openai import OpenAIChat
from agno.models.mistral import MistralChat

# Thread-safe singleton implementation
class _MemoryStorageSingleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._init()
        return cls._instance

    def _init(self):
        # Choose a model for memory (default to groq)
        model_type = DEFAULT_MODEL_TYPE
        model_id = DEFAULT_MODEL_ID
        if model_type.lower() == "gemini":
            model = Gemini(id=model_id)
        elif model_type.lower() == "openai":
            model = OpenAIChat(id=model_id)
        elif model_type.lower() == "mistral":
            model = MistralChat(id=model_id)
        else:
            model = Groq(id=model_id)
        self.memory = Memory(
            model=model,
            db=PostgresMemoryDb(table_name="user_memories", db_url=POSTGRES_CONNECTION),
        )
        self.storage = PostgresStorage(table_name="agent_sessions", db_url=POSTGRES_CONNECTION)


def get_memory():
    return _MemoryStorageSingleton().memory

def get_storage():
    return _MemoryStorageSingleton().storage 