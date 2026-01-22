# Story Template & Generator System - Implementation Summary

## Overview

Successfully implemented a comprehensive story template and generator system that allows:
1. **GUI-based story generation** from predefined templates
2. **AI/LLM integration** with callable tools for programmatic generation
3. **Flexible customization** with character names, locations, and chapter selection
4. **Extensible template library** for different genres and story structures

## Files Created

### Core System

1. **`nico/templates.py`** (550+ lines)
   - `StoryTemplate`, `ChapterTemplate`, `SceneTemplate` data classes
   - `GenreType` enum for categorizing templates
   - `TemplateLibrary` with predefined templates:
     - Classic Romance Novel (10 chapters, 20 scenes)
     - The Hero's Journey (11 chapters, Joseph Campbell's Monomyth)
     - Three-Act Structure (3 acts)

2. **`nico/application/generators.py`** (350+ lines)
   - `StoryGenerator` service class
   - `generate_from_template()` - Creates complete story with all chapters/scenes
   - `add_chapter_from_template()` - Add single chapter to existing story
   - `add_scene_from_template()` - Add single scene to existing chapter
   - `generate_outline_only()` - Preview without database changes
   - `TemplateCustomizer` - Helper for genre-specific customization

3. **`nico/ai_tools.py`** (450+ lines)
   - `STORY_GENERATOR_TOOLS` - OpenAI function calling format tool definitions
   - `AIToolImplementations` - Implementations of all AI-callable functions:
     - `list_story_templates()`
     - `get_template_details(template_name)`
     - `generate_story_from_template(...)` 
     - `add_chapter_to_story(...)`
     - `add_scene_to_chapter(...)`
     - `preview_template_outline(...)`
   - `execute_tool()` - Main entry point for AI tool execution

### User Interface

4. **`nico/presentation/widgets/template_dialog.py`** (400+ lines)
   - `TemplateSelectionDialog` - GUI for selecting and customizing templates
   - Template dropdown with descriptions
   - Genre-specific customization forms:
     - Romance: protagonist, love interest, setting type, occupations
     - Hero's Journey: hero, mentor, villain, quest object
     - Generic: character archetype mapping
   - Chapter skip options
   - Preview outline button
   - Generate story button

5. **Modified: `nico/presentation/main_window.py`**
   - Added menu item: "Project → Generate Story from Template..."
   - Import `TemplateSelectionDialog`
   - `_on_generate_from_template()` method
   - `_generate_story_from_template()` callback
   - Success/error dialogs

6. **Modified: `nico/application/context.py`**
   - Added `story_generator: StoryGenerator` field
   - Initialize `StoryGenerator` in `initialize()` method

### Documentation & Examples

7. **`docs/TEMPLATES.md`** (comprehensive documentation)
   - System overview and philosophy
   - Template descriptions
   - GUI usage instructions
   - AI tool usage with conversation examples
   - Creating custom templates guide
   - Future template suggestions

8. **`examples/ai_story_generation.py`**
   - Complete simulation of AI-user conversation
   - Demonstrates tool calling flow
   - Shows preview, generation, and custom chapter addition

9. **`test_templates.py`**
   - Simple test script to verify template system
   - Lists all templates with details
   - Shows romance novel structure

## Template System Design

### Data Structure Hierarchy

```
StoryTemplate
├── name, genre, description, target_word_count
├── character_archetypes: [{"name": "...", "description": "..."}]
├── location_suggestions: [...]
└── chapters: List[ChapterTemplate]
    ├── number, title, description
    └── scenes: List[SceneTemplate]
        ├── title, order
        ├── beat (story beat name)
        ├── description
        ├── notes (writing guidance)
        ├── required_characters
        └── location_hint
```

### Generated Scene Content Format

When a scene is generated, it includes structured guidance:

```
[BEAT: The Meet-Cute]

Memorable first meeting between protagonist and love interest

Required Characters: Marco, Sofia
Location: The Restaurant

Notes for Writer:
Should be memorable, possibly awkward or contentious

[Write scene here...]
```

## Key Features

### 1. Complete Story Generation
- Generate entire story structure in one operation
- All chapters and scenes created with beat markers
- Character names mapped throughout
- Location suggestions applied
- Skip unwanted chapters

### 2. Incremental Generation
- Add individual chapters to existing stories
- Insert scenes at specific positions
- Useful for filling gaps or adding beats

### 3. Preview Before Generation
- See complete outline without creating records
- Character names applied in preview
- Helps users make informed decisions

### 4. AI Integration
- Tools follow OpenAI function calling format
- Work with any LLM that supports tool/function calling
- Designed for conversational story planning
- Can generate based on natural language discussion

### 5. Customization
- Map character archetypes to actual names
- Customize locations by type
- Choose which chapters to include
- Override story title

## Usage Examples

### GUI Flow
1. User: Click "Project → Generate Story from Template..."
2. Select "Classic Romance Novel" from dropdown
3. Enter protagonist name: "Emma"
4. Enter love interest name: "Liam"
5. Select setting: "Contemporary"
6. Click "Preview Outline" (optional)
7. Click "Generate Story"
8. Result: Complete 10-chapter story with 20 scenes

### AI Conversation Flow

```
User: I want to write a romance about a chef and a food critic

AI: [calls list_story_templates]
    "Perfect! I can help you with the Classic Romance Novel template.
    What are their names?"

User: Marco and Sofia

AI: [calls generate_story_from_template with character_names]
    "I've generated 'A Taste of Love' with 10 chapters covering all the
    key romance beats from meet-cute to happily ever after. Each scene
    includes guidance on what should happen."
```

### Programmatic Usage

```python
from nico.application.context import get_app_context
from nico.templates import TemplateLibrary

app_context = get_app_context()
app_context.initialize()

template = TemplateLibrary.get_romance_novel_template()

story = app_context.story_generator.generate_from_template(
    project=project,
    template=template,
    story_title="My Romance",
    customization={
        "character_names": {
            "Protagonist": "Emma",
            "Love Interest": "Liam"
        }
    }
)

print(f"Created {len(story.chapters)} chapters with {sum(len(ch.scenes) for ch in story.chapters)} scenes")
```

## Romance Novel Template Details

Based on "Romancing the Beat" by Gwen Hayes:

1. **The Setup** - Ordinary world, establish the lack
2. **The Meet-Cute** - First encounter, initial impressions
3. **The Refusal** - Obstacles to relationship
4. **The Connection** - Forced proximity, glimpse of more
5. **Building Attraction** - Growing closer, almost kiss
6. **The First Kiss** - Major romantic milestone
7. **Falling in Love** - Deepening relationship, peak happiness
8. **The Crisis** - Secret revealed, the fight
9. **The Separation** - Break-up, epiphany
10. **The Grand Gesture** - Decision, happily ever after

Each chapter contains 1-2 carefully crafted scenes with:
- Story beat identification
- Scene description
- Required characters
- Location suggestions
- Writing notes

## Hero's Journey Template Details

Joseph Campbell's Monomyth structure:

1. **Ordinary World** - Hero's normal life
2. **Call to Adventure** - The quest is presented
3. **Meeting the Mentor** - Wisdom and tools
4. **Crossing the Threshold** - Point of no return
5. **Tests, Allies, and Enemies** - Learning the rules
6. **Approach to Inmost Cave** - Preparation
7. **The Ordeal** - Greatest fear faced
8. **The Reward** - Treasure/knowledge gained
9. **The Road Back** - Return journey begins
10. **Resurrection** - Final test
11. **Return with Elixir** - Homecoming, new normal

Character archetypes:
- Hero, Mentor, Herald, Threshold Guardian, Shapeshifter, Shadow, Ally/Trickster

## AI Tool Specifications

### Tool: generate_story_from_template

**Input:**
```json
{
  "template_name": "Classic Romance Novel",
  "story_title": "Depths of Love",
  "character_names": {
    "Protagonist": "Dr. Maya Chen",
    "Love Interest": "Jake Rivers"
  },
  "location_names": {
    "Protagonist's Home": "Maya's beachside lab",
    "Workplace/Meeting Ground": "The coral reef research site"
  },
  "skip_chapters": [3]
}
```

**Output:**
```json
{
  "success": true,
  "story_id": 42,
  "story_title": "Depths of Love",
  "chapters_created": 9,
  "total_scenes": 18
}
```

### Tool: add_chapter_to_story

**Input:**
```json
{
  "story_id": 42,
  "chapter_number": 6,
  "chapter_title": "The Underwater World",
  "chapter_description": "Maya takes Jake diving",
  "scenes": [
    {
      "title": "Gearing Up",
      "order": 1,
      "beat": "Preparation",
      "description": "Maya teaches Jake about diving",
      "required_characters": ["Dr. Maya Chen", "Jake Rivers"]
    }
  ]
}
```

**Output:**
```json
{
  "success": true,
  "chapter_id": 123,
  "chapter_number": 6,
  "scenes_created": 1
}
```

## Integration Points

### With Existing Systems

1. **Project Service** - Uses existing project repository
2. **Scene Service** - Creates scenes in database
3. **Binder Widget** - Automatically refreshes to show new stories
4. **Editor Widget** - Can navigate to any generated scene
5. **AI Panel** - Can display these tools in context-aware actions

### With Future Features

1. **Character System** - Will pre-create character entities from archetypes
2. **Location System** - Will pre-create location entities from suggestions
3. **Event/Timeline** - Can mark key beats as timeline events
4. **Notes System** - Beat descriptions can become notes
5. **AI Writing Assistance** - Can use beat guidance to help draft scenes

## Benefits for Users

### For New Writers
- Learn story structure by seeing it in action
- Never forget important beats
- Understand character archetypes
- See how successful stories are built

### For Experienced Writers
- Fast scaffolding for new projects
- Try different structures quickly
- Focus on writing, not structure
- Experiment with genre conventions

### For AI-Assisted Writing
- LLM can understand story structure
- Generate appropriate scaffolding
- Insert missing beats automatically
- Maintain narrative consistency

## Extension Points

### Adding New Templates

1. Create method in `TemplateLibrary`:
```python
@staticmethod
def get_save_the_cat_template() -> StoryTemplate:
    # Define 15 beats...
    return StoryTemplate(...)
```

2. Add to `get_all_templates()`

3. Optionally add customizer in `TemplateCustomizer`

### Adding New Genres

1. Add to `GenreType` enum:
```python
class GenreType(Enum):
    MYSTERY = "mystery"
    SCI_FI = "sci_fi"
    # etc.
```

2. Create template with that genre
3. Create genre-specific customization form in dialog

## Future Enhancements

### Suggested Templates to Add
- Save the Cat! (15 beats)
- Mystery/Whodunit
- Thriller (ticking clock structure)
- Seven-Point Story Structure  
- Dan Harmon's Story Circle
- Genre-specific: Cozy Mystery, Space Opera, Heist, etc.

### Suggested Features
- **Template Editor** - GUI for creating custom templates
- **Template Import/Export** - Share templates as JSON
- **Template Marketplace** - Community template repository
- **Hybrid Templates** - Combine multiple structures
- **Character Pre-generation** - Create character entities from archetypes
- **Location Pre-generation** - Create location entities from suggestions
- **Beat Tracking** - Visualize which beats are complete
- **Structure Validation** - Check if existing story matches template
- **Restructuring Tool** - Transform story from one structure to another

## Technical Implementation Notes

### Database Changes
- Uses existing schema (Project → Story → Chapter → Scene)
- Stores template metadata in `story.metadata` JSON field
- Scene metadata includes template info for tracking

### Performance
- All generation happens in single transaction
- `session.flush()` used to get IDs mid-transaction
- Efficient bulk creation

### Error Handling
- Validates template exists before generation
- Validates project exists
- Returns error dicts from AI tools
- GUI shows error dialogs

### Extensibility
- Template system is pure data (no logic)
- Generator is generic (works with any template)
- AI tools are stateless (easy to test)
- Dialog is genre-aware (can add custom forms)

## Testing

### Manual Testing
1. Run application
2. Select project
3. Click "Project → Generate Story from Template..."
4. Select "Classic Romance Novel"
5. Enter character names
6. Click "Preview Outline"
7. Click "Generate Story"
8. Verify story appears in binder
9. Navigate to scenes
10. Verify content has beat markers and guidance

### Automated Testing
- Run `test_templates.py` to verify templates load
- Run `examples/ai_story_generation.py` to test AI tools
- Use `preview_template_outline()` to test without DB

## Status

✅ **Complete and working:**
- Template library with 3 templates
- Story generator service
- AI tool definitions and implementations
- GUI dialog for template selection
- Menu integration
- Documentation
- Example scripts

🔄 **Ready for:**
- User testing
- Adding more templates
- AI integration (Ollama, OpenAI, etc.)
- Character/location pre-generation
- Custom template creation UI

## Philosophy

The system embodies these principles:

1. **Guidance without constraints** - Templates help but don't limit
2. **Author remains in control** - Every element is customizable
3. **Educational tool** - Shows why beats work
4. **AI-friendly design** - Built for human-AI collaboration
5. **Extensible architecture** - Easy to add templates and genres

The goal is making story structure accessible, especially for AI-assisted writing where the AI can understand and apply narrative patterns in conversation with the writer.
