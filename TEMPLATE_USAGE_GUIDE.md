# Template System Guide

## Overview

The template system provides multi-layer story generation combining:
- **Macro Templates**: Genre-specific story structures (acts, chapters, beats)
- **Micro Templates**: Scene-level tag interpolation with random world-building elements
- **World-Building Tables**: CSV-importable random element lists

## What We've Built

### Domain Models

1. **WorldBuildingTable** (`nico/domain/models/world_building_table.py`)
   - Stores random element lists (names, locations, weather, etc.)
   - Optional weighted selection
   - Methods: `get_random_item()`, `get_random_items(count, allow_duplicates)`

2. **StoryTemplate** (`nico/domain/models/story_template.py`)
   - Macro-level story structure
   - Act structure with chapter ranges
   - Required beats at normalized positions (0.0-1.0)
   - Required scene types per act
   - Symbolic themes
   - Methods: `get_chapter_count()`, `get_beat_at_position()`

3. **SceneTemplate** (`nico/domain/models/scene_template.py`)
   - Scene-level content templates
   - Tag syntax: `{tag}` or `{tag:table.category}`
   - Table mappings: Link tags to WorldBuildingTable references
   - Methods: `extract_tags()`, `interpolate()`, `validate_template()`

### Utilities

1. **CSV Importer** (`nico/application/csv_importer.py`)
   - `import_csv_to_table()`: Import single CSV file
   - `import_csv_with_weights()`: Import with weight column
   - `import_directory_of_csvs()`: Batch import entire directory
   - `export_table_to_csv()`: Export table back to CSV

2. **Seed Templates** (`seed_templates.py`)
   - Pre-built templates for immediate use
   - Mystery Thriller (24 chapters, 3 acts, 10 key beats)
   - Contemporary Romance (20 chapters, 3 acts, 10 key beats)
   - 3 scene templates with tag interpolation

3. **Demo Script** (`demo_templates.py`)
   - Showcases template structure
   - Demonstrates tag interpolation with random values

## Database Structure

Migration `e1e95a525580` added three tables:
- `world_building_tables`: Random element storage
- `story_templates`: Genre-specific story structures
- `scene_templates`: Tag interpolation templates

## Usage Examples

### 1. Seed Example Templates

```bash
python demo_templates.py --seed
```

Creates 2 story templates and 3 scene templates (global, no project).

### 2. View Template Structure

```bash
python demo_templates.py
```

Shows full structure of Mystery Thriller template including:
- Act breakdown with chapter ranges
- Key beats at normalized positions
- Required scene types per act
- Symbolic themes

### 3. Import Your CSV World-Building Data

```python
from nico.application.context import get_app_context
from nico.application.csv_importer import import_csv_to_table

app_context = get_app_context()

# Import single file
import_csv_to_table(
    app_context,
    csv_path="character_names.csv",
    project_id=1,
    table_name="names.fantasy",
    has_header=True,
    column_index=0
)

# Import with weights
import_csv_with_weights(
    app_context,
    csv_path="weather.csv",
    project_id=1,
    table_name="weather.all",
    item_column=0,
    weight_column=1
)

# Batch import directory
import_directory_of_csvs(
    app_context,
    directory="path/to/csv_folder",
    project_id=1
)
```

### 4. Create Story from Template

```python
from nico.domain.models import StoryTemplate, Story, Chapter

app_context = get_app_context()

# Get template
template = app_context._session.query(StoryTemplate).filter_by(
    name="Mystery Thriller"
).first()

# Create story structure
story = Story(
    project_id=1,
    title="Death at Midnight",
    premise="A renowned detective investigates a murder at a luxury hotel"
)
app_context._session.add(story)

# Generate chapters based on template
for chapter_num in range(1, template.get_chapter_count() + 1):
    # Determine act
    act = None
    for act_info in template.act_structure:
        if act_info['chapters'][0] <= chapter_num <= act_info['chapters'][1]:
            act = act_info['act']
            break
    
    chapter = Chapter(
        story_id=story.id,
        chapter_number=chapter_num,
        title=f"Chapter {chapter_num}",
        description=f"Part of Act {act}"
    )
    app_context._session.add(chapter)

app_context._session.commit()
```

### 5. Interpolate Scene Template

```python
from nico.domain.models import SceneTemplate, WorldBuildingTable

app_context = get_app_context()

# Get template
template = app_context._session.query(SceneTemplate).filter_by(
    name="Crime Scene Discovery"
).first()

# Build values from tables
values = {}
for tag, table_ref in template.table_mappings.items():
    table = app_context._session.query(WorldBuildingTable).filter_by(
        project_id=1,
        table_name=table_ref
    ).first()
    
    if table:
        values[tag] = table.get_random_item()

# Add custom values
values["detective"] = "Detective Sarah Chen"
values["victim_name"] = "Marcus Blackwood"

# Interpolate
scene_text = template.interpolate(values)
print(scene_text)
```

## Tag Interpolation Syntax

### Basic Tags
```
{character_name}
{location}
{weather}
```

### Table References (in SceneTemplate.table_mappings)
```python
table_mappings={
    "location": "locations.crime_scene",  # References table_name
    "weather": "weather.ominous",
    "clue": "clues.physical"
}
```

### Extraction & Interpolation
```python
# Auto-extract tags from template_text
tags = template.extract_tags()  # Returns list of tag names

# Fill in values
values = {
    "location": "abandoned warehouse",
    "weather": "gathering fog",
    "clue": "fresh scratches"
}
result = template.interpolate(values)
```

## Mystery Thriller Template Structure

- **Genre**: Mystery
- **Target**: 75,000 words, 24 chapters
- **Acts**:
  - Act 1 (Ch 1-6): Setup & Discovery
  - Act 2 (Ch 7-18): Investigation & Escalation
  - Act 3 (Ch 19-24): Revelation & Resolution

- **Key Beats**:
  - 0.04: Crime Discovery
  - 0.25: Red Herring
  - 0.50: Second Crime (Midpoint)
  - 0.75: Dark Night
  - 0.90: Confrontation
  - 0.96: Justice

## Romance Template Structure

- **Genre**: Romance
- **Target**: 65,000 words, 20 chapters
- **Acts**:
  - Act 1 (Ch 1-5): Meet & Attraction
  - Act 2 (Ch 6-15): Development & Conflict
  - Act 3 (Ch 16-20): Crisis & Resolution

- **Key Beats**:
  - 0.05: Meet Cute
  - 0.25: First Kiss
  - 0.50: Commitment (Midpoint)
  - 0.75: Black Moment
  - 0.90: Grand Gesture
  - 0.98: HEA/HFN

## Next Steps

1. **Template Generation Service**: Create service that generates Story + Chapters from StoryTemplate
2. **Tag Interpolation Engine**: Service that looks up tables and fills templates
3. **Management UI**: Widgets for browsing, creating, editing templates
4. **LLM Integration**: Connect interpolated prompts to LLM for scene content generation
5. **CSV Import UI**: Dialog for batch importing your wife's CSV files

## Architecture Benefits

- **Proven Structure**: Uses well-established story beats (Save the Cat, etc.)
- **Randomization**: CSV tables provide variety while maintaining coherence
- **Layered Context**: 16k coherence threshold addressed through selective retrieval
- **LLM Ready**: Templates become prompts for specialized agents
- **Extensible**: Easy to add new genres, templates, tables

## File Locations

- Models: `nico/domain/models/world_building_table.py`, `story_template.py`, `scene_template.py`
- Utilities: `nico/application/csv_importer.py`
- Seed: `seed_templates.py` (root)
- Demo: `demo_templates.py` (root)
- Migration: `migrations/versions/e1e95a525580_add_templating_and_world_building_tables.py`
