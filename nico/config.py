"""Application configuration and environment setup."""

import os


def disable_telemetry() -> None:
    """
    Disable all telemetry from third-party libraries.
    
    This should be called at application startup before any other imports.
    """
    # Disable ChromaDB/PostHog telemetry
    os.environ["ANONYMIZED_TELEMETRY"] = "False"
    os.environ["POSTHOG_DISABLED"] = "1"
    
    # Disable Hugging Face telemetry
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["HF_HUB_OFFLINE"] = "1"
    
    # Disable any other potential telemetry
    os.environ["DO_NOT_TRACK"] = "1"
