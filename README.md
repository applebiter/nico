# Nico

**Narrative Insight Composition Output**

A privacy-first, local-first writing application for authors, screenwriters, and narrative creators. Think Scrivener meets modern worldbuilding tools, with optional AI assistance that respects your creative process.

---

## For Writers

Nico helps you organize complex narratives across any medium—novels, screenplays, concept albums, video scripts, or non-fiction works.

### What You Get

**Hierarchical Organization**
- Projects contain Stories (or Volumes for non-fiction)
- Stories contain Chapters
- Chapters contain Scenes (fiction) or Sections (non-fiction)
- Drag-and-drop reordering at every level

**Rich Worldbuilding**
- **Characters** with detailed attributes, psychological profiles, and trait sliders
- **Relationships** between characters with customizable dynamics
- **Locations** as rich, character-like entities
- **Events** tracked on flexible timelines (days to decades)
- **Bibliography** for research and citations

**Universal Attachments**
- Add Notes, web Links, and Media (images/audio/video) to any entity
- Attach reference materials directly to scenes, characters, locations, or events

**Professional Features**
- WYSIWYG editor with formatting support
- Import/export: DOCX, Markdown, Fountain, Final Draft, EPUB
- Word count tracking and targets
- Story templates with structural beats
- Automatic revision history

**AI Assistance (Optional)**
- Ollama integration (runs locally on your machine)
- Optional cloud providers (OpenAI, Anthropic, Google)
- Granular control: mark individual items to exclude from AI
- Local-only mode for complete privacy

### Your Data Stays Yours

- **Local-first**: Projects are folders on your computer
- **No cloud sync**: Your stories never leave your machine unless you choose
- **Zero telemetry**: No usage data collected, ever
- **Open source**: Audit the code yourself

---

## For Developers

### Technology Stack

**Backend**
- Python 3.13+
- PostgreSQL with pgvector (for semantic search)
- SQLAlchemy + Alembic (ORM and migrations)
- ChromaDB fallback for vector storage

**Frontend**
- PySide6 (Qt for Python) for native desktop UI
- QWebEngineView hosting ProseMirror/TipTap for rich text editing

**AI Integration**
- Ollama (local models, primary)
- OpenAI / Anthropic / Google APIs (optional)
- Embedding generation for semantic search

**Packaging**
- PyInstaller or Briefcase for cross-platform builds
- Auto-update framework (TBD)

### Architecture

Nico follows clean architecture principles:
- Domain layer: Core entities and business logic
- Application layer: Use cases and services
- Infrastructure layer: Database, AI providers, file I/O
- Presentation layer: Qt UI components

See `ARCHITECTURE.md` (in development) for detailed design decisions.

### Project Structure

```
nico/
├── nico/                  # Main application package
│   ├── domain/           # Entities, value objects, domain services
│   ├── application/      # Use cases, DTOs
│   ├── infrastructure/   # Database, AI clients, file handling
│   └── presentation/     # Qt UI, web editor bridge
├── migrations/           # Alembic database migrations
├── tests/               # Test suite
├── docs/                # Additional documentation
└── pyproject.toml       # Project dependencies
```

### Project-as-Folder Layout

Each user project is a directory containing:
```
my-novel/
├── project.db           # PostgreSQL connection or embedded SQLite
├── media/              # Referenced images, audio, video
├── chroma/             # ChromaDB vector storage (if used)
├── exports/            # Generated output files
└── project.json        # Project manifest
```

### Getting Started (Development)

**Prerequisites**
- Python 3.13+ (managed via pyenv)
- PostgreSQL 15+ with pgvector extension
- Qt6 development libraries

**Setup**
```bash
# Clone the repository
git clone git@github.com:applebiter/nico.git
cd nico

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Set up database
# (Instructions coming soon)

# Run the application
python -m nico
```

### Current Status

🚧 **Early Development** 🚧

We're currently focusing on:
1. ✅ Core database schema design
2. ⏳ SQLAlchemy models and migrations
3. ⏳ Basic Qt UI skeleton
4. ⏳ Project creation and management

See [ROADMAP.md](ROADMAP.md) for planned features and timeline.

---

## Privacy Commitment

Nico disables telemetry from all third-party libraries (ChromaDB/PostHog, Hugging Face) on startup. No data is collected or transmitted unless you explicitly configure and use AI providers.

When AI features are used:
- Data sent only when you invoke AI features
- Respects project-wide "Local-only AI" setting
- Honors per-item "Exclude from AI" flags
- Full transparency over what's sent

See [PRIVACY.md](PRIVACY.md) for complete details.

---

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) (coming soon) for guidelines.

### Development Philosophy
- Privacy is non-negotiable
- Local-first always
- Clean architecture and clear module boundaries
- Comprehensive tests for critical paths
- Document design decisions

---

## License

[MIT License](LICENSE) - see file for details.

---

## Acknowledgments

Built for writers, by developers who respect the creative process. Inspired by Scrivener, enhanced for the AI age, designed for privacy.

---

## Contact

- GitHub Issues: [github.com/applebiter/nico/issues](https://github.com/applebiter/nico/issues)
- Repository: [github.com/applebiter/nico](https://github.com/applebiter/nico)

---

**Status**: Pre-alpha development | **Python**: 3.13+ | **License**: MIT
