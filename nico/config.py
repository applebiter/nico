"""Application configuration and telemetry disabling.

This module must be imported before any third-party libraries that may send telemetry.
"""
import os


def disable_telemetry() -> None:
    """Disable telemetry for all third-party libraries.
    
    Sets environment variables to prevent telemetry collection from:
    - ChromaDB (PostHog analytics)
    - Hugging Face libraries
    - Universal Do Not Track header
    """
    os.environ["ANONYMIZED_TELEMETRY"] = "False"
    os.environ["POSTHOG_DISABLED"] = "1"
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["DO_NOT_TRACK"] = "1"


# Disable telemetry immediately on import
disable_telemetry()
