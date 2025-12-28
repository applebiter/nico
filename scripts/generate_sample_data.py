#!/usr/bin/env python
"""Generate sample project data for testing nico."""

import argparse
import json
import sys
from pathlib import Path
from uuid import UUID

# Add parent directory to path to import nico modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from nico.application.use_cases import (
    CreateChapterUseCase,
    CreateProjectUseCase,
    CreateSceneUseCase,
    CreateStoryUseCase,
    UpdateSceneDocumentUseCase,
)
from nico.infrastructure.persistence import (
    ChapterRepository,
    Database,
    ProjectRepository,
    SceneDocumentRepository,
    SceneRepository,
    StoryRepository,
)


# Sample story data
SAMPLE_STORIES = [
    {
        "title": "The Last Lighthouse",
        "synopsis": "A keeper discovers their lighthouse is the only thing preventing an ancient evil from awakening.",
        "chapters": [
            {
                "title": "Chapter 1: The Arrival",
                "synopsis": "Emma takes up her post at the remote lighthouse.",
                "scenes": [
                    {
                        "title": "The Ferry Ride",
                        "content": "The ferry lurched through gray waters, each wave sending spray across the deck. Emma clutched her single bag tighter, watching the mainland disappear into the mist. The lighthouse rose ahead—a solitary finger of stone pointing at the storm-heavy sky.\n\nShe'd taken the posting without hesitation. Six months of solitude, they'd said. Six months to write, to think, to escape the noise of the city. The pay was modest but the isolation was priceless.\n\nThe ferryman, a grizzled man who'd barely spoken during the journey, finally broke his silence. \"You sure about this, miss? That lighthouse... it has a history.\"\n\nEmma smiled. \"All old places do.\"\n\n\"Aye, but not like this one.\" He spat over the side. \"Last three keepers didn't finish their terms. Left early, they did. Middle of the night, most of 'em.\"\n\nThe lighthouse grew larger, its white walls stark against the darkening sky.",
                    },
                    {
                        "title": "The First Night",
                        "content": "The lighthouse keeper's quarters were sparse but functional. A bed, a desk, a chair, and shelves lined with logbooks dating back a century. Emma ran her fingers along their spines, reading dates: 1923, 1947, 1988, 2003.\n\nShe pulled out the most recent volume. The entries were methodical at first—weather conditions, maintenance notes, supply logs. But as the pages progressed, the handwriting grew erratic. The final entry, dated three months ago, simply read: \"I can't keep the light on anymore. It wants to be dark.\"\n\nEmma closed the book. Superstitious nonsense.\n\nBut that night, as she climbed the spiral stairs to light the beacon for the first time, she felt something watching from the depths below. The light blazed to life, cutting through the darkness, and somewhere far beneath the waves, something ancient stirred.",
                    },
                ],
            },
            {
                "title": "Chapter 2: Strange Tides",
                "synopsis": "Emma begins to notice peculiar patterns in the ocean and the lighthouse's behavior.",
                "scenes": [
                    {
                        "title": "The Morning Discovery",
                        "content": "Emma woke to silence. Wrong silence. The waves that had crashed against the rocks all night were gone. She rushed to the window.\n\nThe ocean was glass-smooth, perfectly still, reflecting the morning sky like a mirror. But it was the wrong color—too dark, almost black, despite the sun.\n\nAnd there were patterns in it. Vast spirals, dozens of them, slowly rotating across the surface. Each one centered around what looked like a deeper darkness, a point of absolute black.\n\nShe grabbed her binoculars. The spirals were moving in perfect synchronization, all rotating the same direction, all pulsing at the same rhythm.\n\nThe lighthouse light, she realized, was still on. She'd turned it off at dawn—she was sure of it. But it blazed behind her, brighter than it should be in daylight.",
                    },
                ],
            },
        ],
    },
    {
        "title": "Debug Story",
        "synopsis": "A quick story for testing basic functionality.",
        "chapters": [
            {
                "title": "Test Chapter",
                "synopsis": "Simple chapter for debugging.",
                "scenes": [
                    {
                        "title": "Test Scene 1",
                        "content": "This is a test scene with minimal content.",
                    },
                    {
                        "title": "Test Scene 2",
                        "content": "Another test scene for navigation testing.",
                    },
                ],
            },
        ],
    },
]


def convert_text_to_prosemirror(text: str) -> str:
    """Convert plain text to ProseMirror JSON format."""
    paragraphs = text.split("\n\n") if text else [""]
    
    content = []
    for para_text in paragraphs:
        if para_text.strip():
            content.append({
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": para_text
                    }
                ]
            })
        else:
            content.append({
                "type": "paragraph"
            })
    
    doc = {
        "type": "doc",
        "content": content
    }
    
    return json.dumps(doc)


def create_sample_project(project_name: str, project_path: Path, author: str = "Test Author") -> None:
    """Create a sample project with dummy data."""
    print(f"Creating sample project: {project_name}")
    print(f"Location: {project_path}")
    
    # Create project directory structure
    full_project_path = project_path / project_name
    full_project_path.mkdir(parents=True, exist_ok=True)
    
    # Initialize database
    db_path = full_project_path / "project.sqlite3"
    db = Database(db_path)
    db.create_tables()
    
    # Create repositories
    session = next(db.get_session())
    project_repo = ProjectRepository(session)
    story_repo = StoryRepository(session)
    chapter_repo = ChapterRepository(session)
    scene_repo = SceneRepository(session)
    scene_doc_repo = SceneDocumentRepository(session)
    
    # Create project
    create_project = CreateProjectUseCase(project_repo, db)
    project = create_project.execute(
        name=project_name,
        path=project_path / project_name,
        description="A sample project with test data for nico",
        author=author,
        local_only_ai=True,
    )
    print(f"✓ Created project: {project.name}")
    
    # Create stories
    for story_data in SAMPLE_STORIES:
        create_story = CreateStoryUseCase(story_repo)
        story = create_story.execute(
            project_id=project.id,
            title=story_data["title"],
            synopsis=story_data["synopsis"],
        )
        print(f"  ✓ Created story: {story.title}")
        
        # Create chapters
        for chapter_data in story_data["chapters"]:
            create_chapter = CreateChapterUseCase(chapter_repo)
            chapter = create_chapter.execute(
                story_id=story.id,
                title=chapter_data["title"],
                synopsis=chapter_data.get("synopsis"),
            )
            print(f"    ✓ Created chapter: {chapter.title}")
            
            # Create scenes
            for scene_data in chapter_data["scenes"]:
                create_scene = CreateSceneUseCase(scene_repo, scene_doc_repo)
                scene = create_scene.execute(
                    chapter_id=chapter.id,
                    title=scene_data["title"],
                )
                print(f"      ✓ Created scene: {scene.title}")
                
                # Add content if provided
                if "content" in scene_data:
                    plain_text = scene_data["content"]
                    content_json = convert_text_to_prosemirror(plain_text)
                    word_count = len(plain_text.split())
                    
                    update_doc = UpdateSceneDocumentUseCase(scene_repo, scene_doc_repo)
                    update_doc.execute(
                        scene_id=scene.id,
                        content=json.loads(content_json),
                        rendered_text=plain_text,
                        word_count=word_count,
                        create_revision=False,
                    )
                    print(f"        ✓ Added content ({word_count} words)")
    
    print(f"\n✓ Sample project created successfully!")
    print(f"  Open it in nico: File → Open Project → {project_path / project_name}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate sample project data for testing nico"
    )
    parser.add_argument(
        "--name",
        default="Sample Project",
        help="Project name (default: Sample Project)"
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=Path.home() / "Documents",
        help="Project parent directory (default: ~/Documents)"
    )
    parser.add_argument(
        "--author",
        default="Test Author",
        help="Author name (default: Test Author)"
    )
    
    args = parser.parse_args()
    
    # Ensure path exists
    args.path.mkdir(parents=True, exist_ok=True)
    
    # Check if project already exists
    project_path = args.path / args.name
    if project_path.exists():
        response = input(f"Project already exists at {project_path}. Overwrite? [y/N] ")
        if response.lower() != 'y':
            print("Aborted.")
            return
        import shutil
        shutil.rmtree(project_path)
    
    try:
        create_sample_project(args.name, args.path, args.author)
    except Exception as e:
        print(f"\n✗ Error creating sample project: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
