# nico Privacy and Telemetry Policy

## Zero Telemetry Guarantee

nico is designed with privacy as a core principle. **No data is collected or transmitted** unless you explicitly configure AI providers.

## What We Disable

The application automatically disables telemetry from all third-party libraries:

### ChromaDB / PostHog
- Environment variables: `ANONYMIZED_TELEMETRY=False`, `POSTHOG_DISABLED=1`
- ChromaDB includes PostHog analytics that can send usage data
- **Status**: Disabled on startup

### Hugging Face Hub
- Environment variables: `HF_HUB_DISABLE_TELEMETRY=1`, `TRANSFORMERS_OFFLINE=1`, `HF_HUB_OFFLINE=1`
- Hugging Face libraries can send model usage telemetry
- **Status**: Disabled on startup

### Universal Do Not Track
- Environment variable: `DO_NOT_TRACK=1`
- Standard privacy header for web requests
- **Status**: Enabled on startup

## How It Works

Telemetry is disabled in [nico/config.py](nico/config.py) which is called **before** any other imports in the application entry point. This ensures no library can send data before being configured.

## AI Providers

When you configure AI providers (OpenAI, Anthropic, Google, Ollama), data is sent **only**:

1. When you explicitly invoke an AI feature
2. According to your project's "Local-only AI" setting
3. Respecting per-item "Exclude from AI" flags

You have full control and transparency over what data is sent to AI services.

## Local-First Architecture

- Your projects are stored as local folders
- Database is SQLite (local file)
- Vector search uses ChromaDB (local folder) or pgvector (your database)
- Media files stored locally
- No cloud sync (by design)

## Audit

You can verify telemetry is disabled by:

1. Checking `nico/config.py` for the `disable_telemetry()` function
2. Setting network monitoring on your system
3. Reviewing application logs (no outbound connections except AI requests you initiate)

## Questions?

If you discover any telemetry we've missed, please open an issue immediately. Privacy is non-negotiable.
