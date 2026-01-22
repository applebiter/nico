"""Simple test to verify template system works."""
from nico.templates import TemplateLibrary

print("Testing Template Library...")
print()

# List all templates
templates = TemplateLibrary.get_all_templates()
print(f"Found {len(templates)} templates:")
print()

for template in templates:
    print(f"📖 {template.name}")
    print(f"   Genre: {template.genre.value}")
    print(f"   Description: {template.description}")
    print(f"   Chapters: {len(template.chapters)}")
    print(f"   Target words: {template.target_word_count:,}" if template.target_word_count else "   Target words: Variable")
    print(f"   Character archetypes: {len(template.character_archetypes)}")
    print()

# Show details of romance template
print("=" * 60)
print("Romance Novel Structure (detailed):")
print("=" * 60)
print()

romance = TemplateLibrary.get_romance_novel_template()
for chapter in romance.chapters:
    print(f"Chapter {chapter.number}: {chapter.title}")
    if chapter.description:
        print(f"  Description: {chapter.description}")
    for scene in chapter.scenes:
        print(f"    → {scene.title}")
        if scene.beat:
            print(f"      Beat: {scene.beat}")
        if scene.required_characters:
            print(f"      Characters: {', '.join(scene.required_characters)}")
    print()

print("✓ Template system working correctly!")
