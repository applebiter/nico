"""Example: AI assistant using story generation tools.

This demonstrates how an LLM would interact with the story generation system
to create a romance novel based on user conversation.
"""
from nico.application.context import get_app_context
from nico.ai_tools import AIToolImplementations


def example_ai_conversation():
    """
    Simulate an AI conversation that generates a story.
    
    This represents what would happen when an AI assistant talks to a user
    about creating a romance novel and then uses the tools to generate it.
    """
    
    # Initialize context
    app_context = get_app_context()
    app_context.initialize()
    
    # Create AI tool implementations
    ai_tools = AIToolImplementations(app_context)
    
    print("=== AI Conversation Simulation ===\n")
    
    # User: "I want to write a romance novel about a marine biologist and a documentary filmmaker"
    print("User: I want to write a romance novel about a marine biologist and a documentary filmmaker")
    print()
    
    # AI: First, list available templates
    print("AI: Let me show you what templates we have available...\n")
    templates = ai_tools.list_story_templates()
    print("Available templates:")
    for t in templates["templates"]:
        print(f"  - {t['name']} ({t['genre']}): {t['chapters']} chapters")
    print()
    
    # AI: Get details about romance template
    print("AI: The Classic Romance Novel template would be perfect. Let me get the details...\n")
    details = ai_tools.get_template_details("Classic Romance Novel")
    print(f"Template: {details['name']}")
    print(f"Target length: ~{details['target_word_count']:,} words")
    print(f"Chapters: {len(details['chapters'])}")
    print("\nKey beats include:")
    for i, chapter in enumerate(details['chapters'][:5], 1):
        print(f"  {i}. {chapter['title']}")
        for scene in chapter['scenes'][:1]:  # Show first scene of each
            if scene['beat']:
                print(f"     - [{scene['beat']}] {scene['title']}")
    print("  ... and more\n")
    
    # User: "Sounds perfect! The biologist is named Dr. Maya Chen and the filmmaker is Jake Rivers"
    print("User: Sounds perfect! The biologist is named Dr. Maya Chen and the filmmaker is Jake Rivers")
    print()
    
    # AI: Preview the outline
    print("AI: Let me show you a preview of the story structure with your characters...\n")
    outline = ai_tools.preview_template_outline(
        template_name="Classic Romance Novel",
        character_names={
            "Protagonist": "Dr. Maya Chen",
            "Love Interest": "Jake Rivers"
        }
    )
    
    print(f"Story: {outline['title']}")
    print(f"\nChapter 1: {outline['chapters'][0]['title']}")
    for scene in outline['chapters'][0]['scenes']:
        print(f"  Scene: {scene['title']}")
        if scene['beat']:
            print(f"    Beat: {scene['beat']}")
        if scene['characters']:
            print(f"    Characters: {', '.join(scene['characters'])}")
    print("  ... (9 more chapters)\n")
    
    # User: "Perfect! Let's generate it. Call the story 'Depths of Love'"
    print("User: Perfect! Let's generate it. Call the story 'Depths of Love'")
    print()
    
    # AI: Generate the actual story
    print("AI: Generating your story structure in the database...\n")
    
    # Get the first project (assuming one exists)
    projects = app_context.project_service.list_projects()
    if not projects:
        print("Error: No project found. Creating a test project first...")
        from nico.domain.models.project import Project
        project = Project(title="Test Project", description="Test project for demo")
        app_context.project_service.create_project(project)
        projects = app_context.project_service.list_projects()
    
    project = projects[0]
    
    result = ai_tools.generate_story_from_template(
        project_id=project.id,
        template_name="Classic Romance Novel",
        story_title="Depths of Love",
        character_names={
            "Protagonist": "Dr. Maya Chen",
            "Love Interest": "Jake Rivers",
            "Best Friend/Confidant": "Sarah"
        },
        location_names={
            "Protagonist's Home": "Maya's beachside lab",
            "Workplace/Meeting Ground": "The coral reef research site",
            "Romantic Date Location": "Sunset pier",
            "Grand Gesture Location": "The research vessel deck"
        }
    )
    
    if result.get("success"):
        print(f"✓ Successfully generated story: {result['story_title']}")
        print(f"  - Story ID: {result['story_id']}")
        print(f"  - Chapters created: {result['chapters_created']}")
        print(f"  - Total scenes: {result['total_scenes']}")
        print()
        print("AI: Your story 'Depths of Love' is ready! I've created the complete structure")
        print("    with 10 chapters and all the key romance beats. Each scene includes:")
        print("    - The story beat it represents (Meet-Cute, First Kiss, Dark Moment, etc.)")
        print("    - What should happen in that scene")
        print("    - Which characters should appear")
        print("    - Location suggestions")
        print("    - Notes to guide your writing")
        print()
        print("    You can now navigate to any scene and start writing!")
    else:
        print(f"Error: {result.get('error')}")
    
    print("\n=== Example: Adding a Custom Chapter ===\n")
    print("User: I want to add a chapter where they go diving together")
    print()
    print("AI: Great idea! Let me add that after the 'Building Attraction' chapter...\n")
    
    # Get the story we just created
    full_project = app_context.project_service.get_project(project.id)
    story = next((s for s in full_project.stories if s.title == "Depths of Love"), None)
    
    if story:
        custom_chapter = ai_tools.add_chapter_to_story(
            story_id=story.id,
            chapter_number=6,
            chapter_title="The Underwater World",
            chapter_description="Maya takes Jake diving to show him her research, leading to a transformative experience",
            scenes=[
                {
                    "title": "Gearing Up",
                    "order": 1,
                    "beat": "Preparation",
                    "description": "Maya teaches Jake about diving and marine life",
                    "required_characters": ["Dr. Maya Chen", "Jake Rivers"]
                },
                {
                    "title": "Beneath the Waves",
                    "order": 2,
                    "beat": "Discovery",
                    "description": "Jake sees Maya in her element, passion for marine life evident",
                    "required_characters": ["Dr. Maya Chen", "Jake Rivers"],
                    "location_hint": "Underwater coral reef"
                },
                {
                    "title": "The Moment",
                    "order": 3,
                    "beat": "Connection",
                    "description": "Underwater, they share a profound moment of connection",
                    "required_characters": ["Dr. Maya Chen", "Jake Rivers"],
                    "notes": "This is a pivotal emotional scene - the underwater setting creates intimacy and wonder"
                }
            ],
            insert_at=6
        )
        
        if custom_chapter.get("success"):
            print(f"✓ Added custom chapter: Chapter {custom_chapter['chapter_number']}")
            print(f"  - Created {custom_chapter['scenes_created']} scenes")
            print()
            print("AI: Perfect! I've added 'The Underwater World' chapter with 3 scenes that")
            print("    show Maya in her element and create a unique bonding moment underwater.")
    
    print("\n=== End Simulation ===")
    
    # Cleanup
    app_context.close()


if __name__ == "__main__":
    example_ai_conversation()
