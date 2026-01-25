"""Demo script to showcase the templating system."""
import sys
from nico.application.context import get_app_context
from seed_templates import seed_all_templates


def demo_story_template():
    """Show off a story template's structure."""
    from nico.domain.models import StoryTemplate
    
    app_context = get_app_context()
    # Get the Mystery Thriller template
    template = app_context._session.query(StoryTemplate).filter_by(
        name="Mystery Thriller"
    ).first()
    
    if not template:
        print("Template not found. Run seed first!")
        return
    
    print("=" * 70)
    print(f"STORY TEMPLATE: {template.name}")
    print("=" * 70)
    print(f"\nGenre: {template.genre}")
    print(f"Target Word Count: {template.target_word_count:,}")
    print(f"\n{template.description}")
    
    print("\n" + "-" * 70)
    print("ACT STRUCTURE:")
    print("-" * 70)
    for act in template.act_structure:
        print(f"\nAct {act['act']}: {act['name']}")
        print(f"  Chapters: {act['chapters'][0]}-{act['chapters'][1]}")
        print(f"  {act['description']}")
    
    print("\n" + "-" * 70)
    print("KEY STORY BEATS (normalized positions):")
    print("-" * 70)
    for beat in template.required_beats:
        chapter = int(beat['position'] * template.get_chapter_count())
        print(f"  {beat['position']:0.2f} (Ch ~{chapter}): {beat['name']}")
        print(f"       → {beat['description']}")
    
    print("\n" + "-" * 70)
    print("REQUIRED SCENE TYPES:")
    print("-" * 70)
    for scene_type in template.required_scenes:
        print(f"  Act {scene_type['act']}: {scene_type['type']}")
        print(f"       → {scene_type['description']}")
    
    print("\n" + "-" * 70)
    print("SYMBOLIC THEMES:")
    print("-" * 70)
    for theme in template.symbolic_themes:
        print(f"  • {theme}")
    
    print("\n")


def demo_scene_template():
    """Show off scene template with tag interpolation."""
    from nico.domain.models import SceneTemplate
    
    app_context = get_app_context()
    # Get the Crime Scene template
    template = app_context._session.query(SceneTemplate).filter_by(
        name="Crime Scene Discovery"
    ).first()
    
    if not template:
        print("Template not found. Run seed first!")
        return
    
    print("=" * 70)
    print(f"SCENE TEMPLATE: {template.name}")
    print("=" * 70)
    print(f"\nType: {template.scene_type}")
    print(f"\n{template.description}")
    
    print("\n" + "-" * 70)
    print("TEMPLATE TEXT:")
    print("-" * 70)
    print(template.template_text)
    
    print("\n" + "-" * 70)
    print("REQUIRED TAGS (extracted automatically):")
    print("-" * 70)
    for tag in sorted(template.required_tags):
        mapping = template.table_mappings.get(tag, "no mapping")
        print(f"  {{{tag}}} → {mapping}")
    
    print("\n" + "-" * 70)
    print("EXAMPLE OUTPUT:")
    print("-" * 70)
    print(template.example_output)
    
    print("\n")


def demo_interpolation(project_id: int):
    """Demo actual tag interpolation with world-building tables."""
    from nico.domain.models import SceneTemplate, WorldBuildingTable
    
    app_context = get_app_context()
    # Get template and tables
    template = app_context._session.query(SceneTemplate).filter_by(
        name="Crime Scene Discovery"
    ).first()
    
    if not template:
        print("Template not found!")
        return
    
    print("=" * 70)
    print("LIVE TAG INTERPOLATION DEMO")
    print("=" * 70)
    print("\nGenerating 3 variations from the same template...\n")
    
    for i in range(1, 4):
        print(f"\n{'='*70}")
        print(f"VARIATION #{i}")
        print('='*70)
        
        # Build value dict from random table selections
        values = {}
        for tag, table_ref in template.table_mappings.items():
            # Look up the table
            table = app_context._session.query(WorldBuildingTable).filter_by(
                project_id=project_id,
                table_name=table_ref
            ).first()
            
            if table:
                values[tag] = table.get_random_item()
            else:
                values[tag] = f"[{tag}]"  # Placeholder if table not found
        
        # Add protagonist name (not from table)
        values["detective"] = "Detective Morrison"
        values["victim_name"] = "Vance"
        
        # Interpolate
        result = template.interpolate(values)
        print(result)
    
    print("\n")


def main():
    """Run the demo."""
    if "--seed" in sys.argv:
        # Seed templates
        print("Seeding templates...")
        app_context = get_app_context()
        # Create as global templates (no project_id)
        seed_all_templates(app_context, project_id=None)
        print("\nTemplates seeded! Run without --seed to see demos.\n")
        return
    
    if "--with-project" in sys.argv:
        # Need project ID for interpolation demo
        try:
            project_id = int(sys.argv[sys.argv.index("--with-project") + 1])
        except (ValueError, IndexError):
            print("Usage: python demo_templates.py --with-project <project_id>")
            print("   or: python demo_templates.py --seed")
            print("   or: python demo_templates.py (for template structure demos)")
            return
        
        app_context = get_app_context()
        # Seed with project-specific tables
        print(f"Seeding for project {project_id}...")
        seed_all_templates(app_context, project_id=project_id)
        
        print("\n" + "=" * 70)
        print("TEMPLATE DEMOS")
        print("=" * 70 + "\n")
        
        demo_story_template()
        demo_scene_template()
        demo_interpolation(project_id)
    else:
        # Just show template structure
        print("\n" + "=" * 70)
        print("TEMPLATE STRUCTURE DEMOS")
        print("=" * 70 + "\n")
        
        demo_story_template()
        demo_scene_template()
        
        print("\nTo see live interpolation demo with random values:")
        print("  python demo_templates.py --with-project <project_id>")
        print("\n")


if __name__ == "__main__":
    main()
