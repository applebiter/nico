# Story Template and Generator System

## Overview

Nico includes a comprehensive library of story structure templates that can automatically generate complete story outlines with chapters, scenes, and story beats. This system is designed to work both with the GUI and with AI assistants that can call generation functions programmatically.

## Features

- **Predefined Templates**: Romance novels, Hero's Journey, Three-Act Structure, and more
- **Customizable Generation**: Map character archetypes to actual names, customize locations
- **AI Integration**: LLM-callable tools for programmatic story generation
- **Flexible Structure**: Generate complete stories or add individual chapters/scenes
- **Beat Sheets**: Each scene includes story beats, required characters, and writer notes

## Available Templates

### Classic Romance Novel
Based on "Romancing the Beat" by Gwen Hayes. 10 chapters covering:
- The Meet-Cute
- Building Attraction
- The First Kiss
- The Crisis and Dark Moment
- The Grand Gesture and HEA

**Character Archetypes**: Protagonist, Love Interest, Best Friend, Antagonist (optional)

### The Hero's Journey
Joseph Campbell's Monomyth in 11 chapters:
- Ordinary World → Call to Adventure
- Meeting the Mentor → Crossing the Threshold
- Tests, Allies, Enemies → The Ordeal
- Resurrection → Return with the Elixir

**Character Archetypes**: Hero, Mentor, Herald, Shadow, Threshold Guardian, Ally/Trickster

### Three-Act Structure
Simple classic structure with Setup, Confrontation, Resolution

## Usage

### GUI Usage

1. **File → Project → Generate Story from Template...**
2. Select a template from the dropdown
3. Customize character names and settings
4. Preview the structure (optional)
5. Click "Generate Story"

The system will create:
- One Story with your specified title
- All chapters from the template
- All scenes with beat markers and guidance
- Placeholder content to guide your writing

### Programmatic Usage (for AI Assistants)

The system exposes tools that AI assistants can call to generate stories based on conversation with users.

#### Example Conversation Flow

```
User: "I want to write a romance novel about a chef and a food critic"

AI: Let me help you generate a romance story structure. What are their names?

User: "The chef is named Marco and the critic is Sofia"

AI: [calls generate_story_from_template with:
  template_name: "Classic Romance Novel",
  story_title: "A Taste of Love",
  character_names: {
    "Protagonist": "Marco",
    "Love Interest": "Sofia"
  }
]

System: Created story with 10 chapters and 20 scenes

AI: I've generated "A Taste of Love" with 10 chapters following the classic 
romance structure. The story includes key beats like the meet-cute, first kiss, 
dark moment, and happily ever after. Each scene has guidance on what should 
happen and which characters appear.
```

## AI Tool Definitions

### list_story_templates()
Returns all available templates with descriptions

### get_template_details(template_name)
Get full details of a template including all chapters, scenes, and beats

### generate_story_from_template(template_name, story_title, character_names, location_names, skip_chapters)
Generate complete story structure in the database

### add_chapter_to_story(story_id, chapter_number, chapter_title, scenes, insert_at)
Add a single chapter to an existing story

### add_scene_to_chapter(chapter_id, scene_title, scene_order, beat, description, required_characters)
Add a single scene to an existing chapter

### preview_template_outline(template_name, character_names)
Preview what would be generated without creating database records

## Template Structure

Each template defines:

```python
StoryTemplate(
    name="Template Name",
    genre=GenreType.ROMANCE,
    description="What this template is for",
    target_word_count=80000,
    chapters=[...],  # List of ChapterTemplate objects
    character_archetypes=[...],  # Character roles needed
    location_suggestions=[...],  # Location types
)
```

### Chapter Structure

```python
ChapterTemplate(
    number=1,
    title="Chapter Title",
    description="What happens in this chapter",
    scenes=[...]  # List of SceneTemplate objects
)
```

### Scene Structure

```python
SceneTemplate(
    title="Scene Title",
    order=1,
    beat="Story Beat Name",  # e.g., "The Meet-Cute", "Dark Moment"
    description="What should happen in this scene",
    notes="Writing guidance for the author",
    required_characters=["Protagonist", "Love Interest"],
    location_hint="Where this scene takes place"
)
```

## Generated Content

When a scene is generated, it includes:

```
[BEAT: The Meet-Cute]

Memorable first meeting between protagonist and love interest

Required Characters: Marco, Sofia
Location: The Restaurant

Notes for Writer:
Should be memorable, possibly awkward or contentious

[Write scene here...]
```

This gives writers clear guidance on:
- Which story beat this scene represents
- What should happen
- Who should be present
- Where it takes place
- Tips for making it effective

## Creating Custom Templates

To add your own templates:

1. Edit `nico/templates.py`
2. Create a new `@staticmethod` in `TemplateLibrary`:

```python
@staticmethod
def get_my_custom_template() -> StoryTemplate:
    chapters = [
        ChapterTemplate(
            number=1,
            title="Opening",
            scenes=[
                SceneTemplate(
                    title="Hook",
                    order=1,
                    beat="Opening Image",
                    description="Establish world and character"
                )
            ]
        )
    ]
    
    return StoryTemplate(
        name="My Custom Template",
        genre=GenreType.CUSTOM,
        description="Description of structure",
        target_word_count=75000,
        chapters=chapters,
        character_archetypes=[...],
        location_suggestions=[...]
    )
```

3. Add it to `get_all_templates()`:

```python
@staticmethod
def get_all_templates() -> List[StoryTemplate]:
    return [
        TemplateLibrary.get_romance_novel_template(),
        TemplateLibrary.get_heros_journey_template(),
        TemplateLibrary.get_my_custom_template(),  # Add yours
    ]
```

## Future Templates to Add

- **Save the Cat!** (Blake Snyder's 15 beats)
- **Mystery/Whodunit** (Clue planting, red herrings, reveal)
- **Thriller** (Ticking clock, escalating tension)
- **Seven-Point Story Structure**
- **Freytag's Pyramid**
- **Dan Harmon's Story Circle**
- **Genre-specific**:
  - Cozy Mystery
  - Space Opera
  - Regency Romance
  - Young Adult Coming-of-Age
  - Heist Story
  - Revenge Tragedy

## Integration with AI Panel

The AI Tools panel in Nico's right sidebar can use these tools to:

1. Suggest appropriate templates based on user's story idea
2. Generate story structure after discussing characters
3. Add missing beats or chapters to existing stories
4. Help restructure stories that aren't working

Example AI interaction:
```
User: "My story is dragging in the middle"

AI: [calls get_template_details for current genre]
AI: "Looking at your story structure, you're missing the Midpoint beat 
where the stakes should escalate. Would you like me to add a chapter 
that raises the tension?"

User: "Yes, please"

AI: [calls add_chapter_to_story with Midpoint scene templates]
```

## Benefits

- **Faster Drafting**: Structure is laid out, just fill in the scenes
- **Beat Awareness**: Never miss key story moments
- **Flexibility**: Skip chapters, customize names, modify structure
- **Learning Tool**: See how successful story structures work
- **AI Collaboration**: LLMs can help generate and refine structure
- **Consistency**: All stories follow proven narrative patterns

## Philosophy

The template system follows these principles:

1. **Guidance, not constraints**: Templates provide structure but don't limit creativity
2. **Author control**: Every element can be customized or skipped
3. **Educational**: Templates show why beats work and when to use them
4. **AI-friendly**: Designed for both human and AI interaction
5. **Extensible**: Easy to add new templates for different genres and styles

The goal is to make story structure accessible and actionable, especially for new writers or when working with AI assistants that can understand and apply narrative patterns.
