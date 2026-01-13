"""Tests for configuration and telemetry disabling."""
import os


def test_telemetry_disabled() -> None:
    """Verify that telemetry environment variables are set correctly."""
    from nico import config
    
    # These should be set by config module on import
    assert os.environ.get("ANONYMIZED_TELEMETRY") == "False"
    assert os.environ.get("POSTHOG_DISABLED") == "1"
    assert os.environ.get("HF_HUB_DISABLE_TELEMETRY") == "1"
    assert os.environ.get("DO_NOT_TRACK") == "1"
