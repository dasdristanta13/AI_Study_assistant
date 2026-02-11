"""
Tracing Utilities
Handles Langfuse integration for LangGraph tracing
"""
import os
from typing import Optional, List
from langfuse.langchain import CallbackHandler
from app.core.config import Config


class TracingManager:
    """Manage tracing configuration and callbacks"""
    
    def __init__(self):
        self.tracing_enabled = self._check_enabled()
        self.handler = None
        
        if self.tracing_enabled:
            self._initialize_handler()
    
    def _check_enabled(self) -> bool:
        """Check if tracing is enabled via config or env"""
        # Check env var first (override), then config
        env_enable = os.getenv("TRACING_ENABLED", "").lower() == "true"
        return env_enable or Config.TRACING_ENABLED
    
    def _initialize_handler(self):
        """Initialize Langfuse callback handler"""
        try:
            public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
            secret_key = os.getenv("LANGFUSE_SECRET_KEY")
            
            if public_key and secret_key:
                self.handler = CallbackHandler(
                    public_key=public_key,
                    secret_key=secret_key,
                    host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
                )
                print("✓ Langfuse tracing enabled")
            else:
                print("! Tracing enabled but keys missing. Tracing skipped.")
                self.tracing_enabled = False
        except Exception as e:
            print(f"x Failed to initialize Langfuse: {e}")
            self.tracing_enabled = False
            self.handler = None

    def get_callbacks(self) -> List[CallbackHandler]:
        """Get tracing callbacks if enabled"""
        if self.tracing_enabled and self.handler:
            return [self.handler]
        return []

    def flush(self):
        """Flush traces"""
        if self.tracing_enabled and self.handler:
            self.handler.flush()
