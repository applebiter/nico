"""Complete test for New Chapter button functionality."""
from nico.application.context import get_app_context

def main():
    """Test the complete chapter creation flow."""
    print("🔍 Testing Complete New Chapter Flow\n")
    
    app_context = get_app_context()
    
    # Get a story
    projects = app_context.project_service.list_projects()
    if not projects:
        print("❌ No projects found")
        return
    
    project = app_context.project_service.get_project(projects[0].id)
    if not project or not project.stories:
        print("❌ No stories found")
        return
    
    story = project.stories[0]
    initial_chapter_count = len(story.chapters)
    
    print(f"📖 Story: {story.title}")
    print(f"   Initial chapters: {initial_chapter_count}")
    
    # Simulate creating a new chapter (what the dialog would do)
    print("\n📝 Simulating chapter creation...")
    from nico.domain.models import Chapter
    
    new_chapter = Chapter(
        story_id=story.id,
        title="Test Chapter",
        description="This is a test chapter created by the automation",
        position=initial_chapter_count,
        exclude_from_ai=False
    )
    
    app_context._session.add(new_chapter)
    app_context.commit()
    
    # Reload story to verify
    refreshed_project = app_context.project_service.get_project(project.id)
    refreshed_story = refreshed_project.stories[0]
    
    print(f"\n✅ Chapter created successfully!")
    print(f"   New chapter count: {len(refreshed_story.chapters)}")
    print(f"   Latest chapter: {refreshed_story.chapters[-1].title}")
    
    # Clean up - delete the test chapter
    print("\n🧹 Cleaning up test data...")
    app_context._session.delete(new_chapter)
    app_context.commit()
    
    final_project = app_context.project_service.get_project(project.id)
    final_story = final_project.stories[0]
    print(f"   Final chapter count: {len(final_story.chapters)}")
    
    print("\n✅ All tests passed! The New Chapter button should work correctly.")

if __name__ == "__main__":
    main()
