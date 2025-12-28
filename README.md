# nico - Narrative Insight Composition Output

A local-first writing application for long-form fiction with Scrivener-like UX, AI assistance, and comprehensive worldbuilding tools.

## Features

- **Hierarchical project structure**: Project → Story → Chapter → Scene
- **Rich text editor** with screenplay support (Fountain/Final Draft)
- **Worldbuilding entities**: Characters, Locations, Events with detailed attributes
- **Universal attachments**: Notes, Links, and Media can be attached to any entity
- **Autosave** and automatic revision history
- **AI integration**: Ollama-first with privacy controls
- **Full-text and semantic search**
- **Multi-format import/export**: DOCX, Markdown, Fountain, Final Draft XML, EPUB
- **Bibliography management**: BibTeX support with CSL formatting
- **Zero telemetry**: All third-party telemetry is disabled by default

## Installation

```bash
# Clone the repository
git clone https://github.com/applebiter/nico.git
cd nico

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black nico tests

# Type checking
mypy nico
```

## Usage

```bash
# Run the application
python -m nico
```

## Privacy

nico takes your privacy seriously. All third-party telemetry is **disabled by default**:

- ChromaDB/PostHog analytics: **OFF**
- Hugging Face telemetry: **OFF**
- All tracking headers: **OFF**

The application sets these environment variables on startup:
- `ANONYMIZED_TELEMETRY=False`
- `POSTHOG_DISABLED=1`
- `HF_HUB_DISABLE_TELEMETRY=1`
- `DO_NOT_TRACK=1`

Your writing stays on your machine. Period.

## Project Structure

- `nico/domain/` - Business logic and entities
- `nico/application/` - Use cases and application services
- `nico/infrastructure/` - External adapters (database, AI, file I/O)
- `nico/presentation/` - UI components (PySide6/Qt)

## License

MIT License - See [LICENSE](LICENSE) for details.

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.
