# LLM Team Feature

## Overview

Nico's LLM Team feature allows you to build a flexible "team" of AI assistants, mixing local and cloud-based models. This gives you fine-grained control for expert workflows while remaining simple for casual use.

## Architecture

### Modules

- **`nico/ai/providers.py`** - Multi-provider LLM abstraction
- **`nico/ai/discovery.py`** - Network discovery for Ollama endpoints
- **`nico/ai/manager.py`** - Team coordination and routing
- **`nico/application/ai_service.py`** - Qt-friendly async service wrapper
- **`nico/presentation/widgets/llm_team_dialog.py`** - Configuration wizard

### Supported Providers

1. **Ollama** (localhost or LAN)
   - Endpoint: `http://ip:11434/api/generate`
   - Auto-discovery via network scanning
   - Support for any Ollama model
   
2. **OpenAI**
   - Endpoint: `https://api.openai.com/v1/chat/completions`
   - Models: GPT-4o, GPT-4 Turbo, GPT-3.5 Turbo, etc.
   
3. **Anthropic Claude**
   - Endpoint: `https://api.anthropic.com/v1/messages`
   - Models: Claude 3.5 Sonnet, Claude 3.5 Haiku, Claude 3 Opus
   
4. **Google Gemini**
   - Endpoint: `https://generativelanguage.googleapis.com/v1/models`
   - Models: Gemini 2.0 Flash, Gemini 1.5 Pro, Gemini 1.5 Flash
   
5. **xAI Grok**
   - Endpoint: `https://api.x.ai/v1/chat/completions`
   - Models: Grok Beta, Grok 2

## Configuration

### Accessing the Configuration

**Tools → Configure AI Team...**

### Setup Workflow

1. **Team Members Tab**
   - View existing team members
   - Enable/disable individual AIs
   - Set primary AI (used by default)
   - Configure speed tier (fast/medium/slow) and cost tier (free/low/medium/high)

2. **Discover Ollama Tab**
   - Automatically scan your local network for Ollama instances
   - Shows hostname, IP, and available models
   - One-click add discovered models to your team
   
3. **Add API Provider Tab**
   - Quick-add forms for cloud providers
   - Enter API key and select model
   - Instantly add to team

### Example Team

A typical power-user team might look like:

- **Primary**: `ollama_workstation_qwen2.5:32b` (local beefy machine)
  - Speed: slow, Cost: free
  - Use for: Creative writing, deep analysis
  
- **Fast Local**: `ollama_laptop_ministral:3b` (local laptop)
  - Speed: fast, Cost: free
  - Use for: Quick suggestions, grammar checks
  
- **Cloud Fallback**: `openai_gpt-4o-mini` (OpenAI API)
  - Speed: medium, Cost: low
  - Use for: When local models are busy or unavailable

- **Specialty**: `anthropic_claude-3-5-sonnet` (Anthropic API)
  - Speed: medium, Cost: medium
  - Use for: Character dialogue, nuanced voice

## Using the Team

### From the AI Panel

The AI panel (right side of Nico) has a **Model Selector** dropdown showing all enabled team members:

- ⭐ = Primary model
- ✓ = Available model
- 💤 = Disabled model

Select a model and:
- Use **Quick Actions** for context-aware tasks
- Use **Chat** for freeform conversation

### Automatic Fallback

If you use the primary model and it fails (offline, busy, error), Nico automatically tries other enabled team members in order until one succeeds.

### Smart Routing (Advanced)

The `LLMTeam` class supports task-based routing:

```python
from nico.ai.manager import get_llm_team

team = get_llm_team()

# Route by task type
response = await team.route_by_task(
    prompt="Fix this grammar: 'me and him went to the store'",
    task_type="quick"  # Uses fast, cheap models
)

response = await team.route_by_task(
    prompt="Write a dramatic character revelation scene",
    task_type="creative"  # Uses slower, more capable models
)
```

Task types:
- **quick**: Grammar, spelling, simple suggestions → fast models
- **creative**: Story writing, character development → medium/slow models
- **analytical**: Plot analysis, continuity checks → models with function calling
- **coding**: Template generation, tool usage → models with function calling

### Parallel Generation

Get multiple perspectives:

```python
responses = await team.parallel_generate(
    prompt="Suggest a title for this chapter",
    llm_ids=["local_fast", "cloud_creative", "primary"]
)

# responses is dict: {"local_fast": "...", "cloud_creative": "...", "primary": "..."}
```

## Capabilities

### Speed Tiers

- **fast**: Small models (3B-8B parameters), <2s response time
- **medium**: Mid-size models (13B-20B parameters), 2-5s response time  
- **slow**: Large models (32B+ parameters), 5-15s response time

### Cost Tiers

- **free**: Local Ollama models, no API cost
- **low**: Cheap API models (GPT-3.5, GPT-4o-mini, Claude Haiku, Gemini Flash)
- **medium**: Standard API models (GPT-4, Claude Sonnet)
- **high**: Premium API models (Claude Opus, GPT-4 Turbo)

### Feature Support

- **Streaming**: Real-time token-by-token generation (all providers)
- **Function Calling**: Use AI-callable tools (OpenAI, Anthropic, Google only)

## Network Discovery

### How It Works

1. Detects your local subnet (e.g., `192.168.1.0/24`)
2. Concurrently checks each IP for Ollama service on port 11434
3. Queries `/api/tags` to get available models
4. Returns list of discovered endpoints with metadata

### Manual Discovery

If auto-discovery doesn't find your Ollama instance:

1. Go to **Discover Ollama** tab
2. Enter subnet manually (e.g., `192.168.50.0/24`)
3. Click **Scan Network**

Or add manually from **Team Members** tab → **Add Member**.

## Warmup

"Warming up" a model means sending a small test prompt to:
- Load the model into memory/GPU
- Verify connectivity
- Ensure fast response for subsequent requests

Especially useful for local Ollama models that aren't kept in memory.

**Tools → Configure AI Team → Warm Up All**

## Context & Memory Management

### Context Awareness

The AI panel automatically includes context based on what you're viewing:

- **Project**: World/universe information, all stories
- **Story**: Plot, structure, chapters
- **Chapter**: Scenes, beats, flow
- **Scene**: Actual prose, characters present, location

### Conversation Memory (Coming Soon)

Future enhancements:
- Per-context conversation history
- Long-term project memory (character traits, world rules)
- Context window management (automatic truncation)
- Memory persistence across sessions

## API Keys & Security

API keys are stored in `~/.nico/preferences.json`:

```json
{
  "llm_team": {
    "members": [
      {
        "id": "openai_gpt4",
        "name": "OpenAI GPT-4",
        "provider": "openai",
        "api_key": "sk-...",
        ...
      }
    ]
  }
}
```

**Security Note**: Keys are stored in plaintext. Ensure file permissions are restrictive:

```bash
chmod 600 ~/.nico/preferences.json
```

## Troubleshooting

### "No AI configured"

You haven't added any team members yet. Go to **Tools → Configure AI Team** and add at least one provider.

### "Error: Connection refused"

- **Ollama**: Ensure Ollama is running (`ollama serve`)
- **API**: Check internet connection and API key validity

### "Model not found"

Ollama model not downloaded. Run:
```bash
ollama pull mistral:3b
```

### Discovery finds no endpoints

- Ensure Ollama is running on target machine
- Check firewall (port 11434 must be open)
- Verify you're on the same network
- Try manual discovery with correct subnet

### Slow responses

- Check model size (large models = slow)
- Network latency for remote Ollama
- API rate limits for cloud providers
- Consider adding a "fast" tier model for quick tasks

## Developer API

### Adding a New Provider

1. Create a subclass of `BaseLLMProvider` in `providers.py`
2. Implement `check_availability()`, `generate()`, `stream()`
3. Add to `create_provider()` factory
4. Add to `ProviderType` enum
5. Update `llm_team_dialog.py` with UI controls

Example:

```python
class CustomProvider(BaseLLMProvider):
    async def check_availability(self) -> bool:
        # Verify endpoint is reachable
        ...
    
    async def generate(self, prompt: str, **kwargs) -> str:
        # Call your API
        ...
    
    async def stream(self, prompt: str, **kwargs):
        # Yield tokens as they arrive
        ...
```

### Using the Team Programmatically

```python
from nico.ai.manager import get_llm_team
from nico.ai.providers import LLMConfig, ProviderType

team = get_llm_team()

# Add a member
config = LLMConfig(
    id="my_llm",
    name="My Custom LLM",
    provider=ProviderType.OLLAMA,
    model="llama2:13b",
    endpoint="http://192.168.1.100:11434",
    speed_tier="medium",
    cost_tier="free"
)
team.add_member(config)

# Generate with fallback
response = await team.generate_with_fallback(
    prompt="Write a haiku about coding",
    preferred_ids=["my_llm", "primary"]
)

# Save to preferences
from nico.preferences import get_preferences
prefs = get_preferences()
prefs.llm_team = team.to_dict()
prefs.save()
```

## Roadmap

- [ ] Streaming responses in UI
- [ ] Token usage tracking
- [ ] Cost estimation
- [ ] Model-specific settings (temperature, top_p, etc.)
- [ ] Custom system prompts per context level
- [ ] Long-term memory with vector search
- [ ] Tool calling integration with story generators
- [ ] Conversation history export
- [ ] Team presets ("Writing Team", "Editing Team", etc.)
- [ ] Background model warmup on startup

## Philosophy

**One AI is enough.** You don't need a team to use Nico effectively. A single local Ollama model or cloud API will do everything.

**But a team is powerful.** If you want:
- Fast feedback (small local model)
- Creative depth (large model)
- Cost control (free local, fallback to paid)
- Redundancy (local fails → cloud backup)

Then build your team. The system scales from 1 to many seamlessly.
