"""Test script to verify chapter dialog functionality."""
from PySide6.QtWidgets import QApplication
from nico.presentation.widgets.chapter_dialog import ChapterDialog
from nico.application.context import get_app_context

def main():
    """Test the chapter dialog."""
    print("🔍 Testing Chapter Dialog\n")
    
    app = QApplication([])
    app_context = get_app_context()
    
    # Get a story to test with
    projects = app_context.project_service.list_projects()
    if not projects:
        print("❌ No projects found")
        return
    
    project = app_context.project_service.get_project(projects[0].id)
    if not project or not project.stories:
        print("❌ No stories found")
        return
    
    story = project.stories[0]
    print(f"📖 Testing with story: {story.title}")
    print(f"   Current chapters: {len(story.chapters)}")
    
    # Test creating a new chapter dialog (don't show it, just verify it can be instantiated)
    try:
        dialog = ChapterDialog(story.id)
        print("\n✅ ChapterDialog created successfully!")
        print(f"   Dialog title: {dialog.windowTitle()}")
        print(f"   Story ID: {dialog.story_id}")
        print(f"   Is editing: {dialog.is_editing}")
    except Exception as e:
        print(f"\n❌ Error creating dialog: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
