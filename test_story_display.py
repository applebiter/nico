"""Test script to verify stories are loaded correctly in project overview."""
from nico.application.context import get_app_context

def main():
    """Test loading project with stories."""
    print("🔍 Testing Project Overview Story Display\n")
    
    app_context = get_app_context()
    
    # Get all projects
    projects = app_context.project_service.list_projects()
    print(f"Found {len(projects)} project(s)")
    
    if not projects:
        print("❌ No projects found in database")
        return
    
    # Get the first project with full details
    project = app_context.project_service.get_project(projects[0].id)
    
    if not project:
        print("❌ Could not load project details")
        return
    
    print(f"\n📚 Project: {project.title}")
    print(f"   Description: {project.description or 'N/A'}")
    print(f"   Stories: {len(project.stories)}")
    
    if not project.stories:
        print("\n❌ No stories found in project")
        return
    
    print("\n📖 Stories in project:")
    for story in project.stories:
        chapter_count = len(story.chapters)
        scene_count = sum(len(chapter.scenes) for chapter in story.chapters)
        word_count = sum(
            scene.word_count
            for chapter in story.chapters
            for scene in chapter.scenes
        )
        
        print(f"   • {story.title}")
        print(f"     Chapters: {chapter_count}, Scenes: {scene_count}, Words: {word_count:,}")
    
    print("\n✅ Stories should now be visible in the Project Overview widget!")

if __name__ == "__main__":
    main()
