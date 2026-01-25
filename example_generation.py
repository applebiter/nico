"""Example: Generate a complete mystery story structure from template."""
from nico.application.context import get_app_context
from nico.domain.models import StoryTemplate, Story, Chapter


def generate_story_from_template(
    project_id: int,
    template_name: str,
    story_title: str,
    story_description: str
) -> Story:
    """Generate a complete story structure from a template.
    
    Creates:
    - Story record
    - All chapters based on template structure
    - Placeholder scenes at key beat positions
    
    Args:
        project_id: Project to create story in
        template_name: Name of story template to use
        story_title: Title for the new story
        story_description: Story description/synopsis
        
    Returns:
        Created Story with chapters
    """
    app_context = get_app_context()
    
    # Get template
    template = app_context._session.query(StoryTemplate).filter_by(
        name=template_name
    ).first()
    
    if not template:
        raise ValueError(f"Template '{template_name}' not found")
    
    print(f"Generating story from template: {template.name}")
    print(f"Target structure: {template.get_chapter_count()} chapters, {template.target_word_count:,} words\n")
    
    # Create story
    story = Story(
        project_id=project_id,
        title=story_title,
        description=story_description,
        word_count_target=template.target_word_count,
        is_fiction=True
    )
    app_context._session.add(story)
    app_context._session.flush()  # Get story.id
    
    print(f"Created story: {story.title}")
    print(f"Story ID: {story.id}\n")
    
    # Generate chapters
    chapter_count = template.get_chapter_count()
    chapters_created = []
    
    for chapter_num in range(1, chapter_count + 1):
        # Determine which act this chapter belongs to
        act_info = None
        for act in template.act_structure:
            if act['chapters'][0] <= chapter_num <= act['chapters'][1]:
                act_info = act
                break
        
        # Check if this chapter has special templates
        chapter_template = template.chapter_structure.get('chapter_templates', {}).get(str(chapter_num))
        
        # Build chapter title based on structure
        if chapter_template:
            chapter_title = f"Chapter {chapter_num}: {chapter_template['type'].replace('_', ' ').title()}"
        else:
            chapter_title = f"Chapter {chapter_num}"
        
        # Build description
        description_parts = [f"Act {act_info['act']}: {act_info['name']}"]
        
        if chapter_template:
            description_parts.append(f"Type: {chapter_template['type']}")
            if 'required_elements' in chapter_template:
                elements = ', '.join(chapter_template['required_elements'])
                description_parts.append(f"Required: {elements}")
        
        chapter = Chapter(
            story_id=story.id,
            number=chapter_num,
            title=chapter_title,
            description='\n'.join(description_parts)
        )
        app_context._session.add(chapter)
        chapters_created.append(chapter)
    
    app_context._session.commit()
    
    print(f"Created {len(chapters_created)} chapters:\n")
    
    # Show structure
    for act in template.act_structure:
        act_chapters = [c for c in chapters_created 
                       if act['chapters'][0] <= c.number <= act['chapters'][1]]
        print(f"  Act {act['act']}: {act['name']}")
        print(f"  Chapters {act['chapters'][0]}-{act['chapters'][1]} ({len(act_chapters)} chapters)")
        print(f"  {act['description']}")
        print()
    
    # Show key beats
    print("Key story beats will occur at:")
    for beat in template.required_beats:
        chapter_num = int(beat['position'] * chapter_count)
        if 0 < chapter_num <= chapter_count:
            print(f"  Ch {chapter_num}: {beat['name']} ({beat['position']:.0%})")
            print(f"           → {beat['description']}")
    
    print(f"\nStory '{story.title}' created successfully!")
    print(f"Next: Add scenes to chapters and use scene templates to generate content")
    
    return story


def example_mystery_generation():
    """Example: Generate a mystery thriller."""
    story = generate_story_from_template(
        project_id=1,
        template_name="Mystery Thriller",
        story_title="The Midnight Files",
        story_description="When a prominent journalist is found dead with classified files, "
                     "Detective Morrison must navigate a web of corporate conspiracy and government secrets."
    )
    return story


def example_romance_generation():
    """Example: Generate a contemporary romance."""
    story = generate_story_from_template(
        project_id=1,
        template_name="Contemporary Romance",
        story_title="Write Your Heart Out",
        story_description="A bestselling romance author and a grumpy literary critic are forced to co-write "
                     "a book together—and discover that their on-page chemistry is nothing compared to real life."
    )
    return story


if __name__ == "__main__":
    import sys
    
    if "--mystery" in sys.argv:
        example_mystery_generation()
    elif "--romance" in sys.argv:
        example_romance_generation()
    else:
        print("Generate a complete story structure from a template.")
        print("\nUsage:")
        print("  python example_generation.py --mystery")
        print("  python example_generation.py --romance")
        print("\nThis will create a Story with all chapters structured according to the template.")
