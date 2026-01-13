"""Test script to explore and verify database models."""
from datetime import datetime

from nico.infrastructure.database import init_db, settings
from nico.domain.models import (
    Project,
    Story,
    Chapter,
    Scene,
    Character,
    Location,
    Event,
    Relationship,
)


def main():
    """Create sample data and explore the database."""
    print("🚀 Initializing Nico database connection...")
    db = init_db(settings.get_database_url())
    
    print(f"✅ Connected to: {settings.get_database_url().split('@')[1]}\n")
    
    # Create a session
    session = db.SessionLocal()
    
    try:
        # Create a Project
        print("📚 Creating project...")
        project = Project(
            title="The Shadow Chronicles",
            description="A fantasy trilogy about a young mage discovering an ancient conspiracy",
            author="Test Author",
            meta={"local_only_ai": True, "target_word_count": 300000}
        )
        session.add(project)
        session.flush()
        print(f"   ✓ Project created: {project}")
        
        # Create a Story
        print("\n📖 Creating story...")
        story = Story(
            project_id=project.id,
            title="Book One: The Awakening",
            subtitle="Shadows Stir",
            description="A young apprentice discovers forbidden magic",
            is_fiction=True,
            word_count_target=100000,
            position=0,
            meta={"genre": "fantasy", "setting": "medieval"}
        )
        session.add(story)
        session.flush()
        print(f"   ✓ Story created: {story}")
        
        # Create Chapters
        print("\n📑 Creating chapters...")
        chapter1 = Chapter(
            story_id=story.id,
            title="The Apprentice",
            description="Introduction to our protagonist",
            number=1,
            position=0
        )
        chapter2 = Chapter(
            story_id=story.id,
            title="The Discovery",
            description="Finding the ancient tome",
            number=2,
            position=1
        )
        session.add_all([chapter1, chapter2])
        session.flush()
        print(f"   ✓ Chapter 1: {chapter1.title}")
        print(f"   ✓ Chapter 2: {chapter2.title}")
        
        # Create Scenes
        print("\n✍️  Creating scenes...")
        scene1 = Scene(
            chapter_id=chapter1.id,
            title="Morning in the Tower",
            content="<p>Elara gazed out the tower window as dawn broke over the mountains...</p>",
            word_count=1250,
            beat="Opening image",
            position=0,
            meta={"pov": "Elara", "setting": "Mage Tower", "tags": ["establishing"]}
        )
        scene2 = Scene(
            chapter_id=chapter1.id,
            title="The Master's Lesson",
            content="<p>Master Theron's voice echoed through the stone chamber...</p>",
            word_count=890,
            beat="Inciting incident",
            position=1,
            meta={"pov": "Elara", "setting": "Training Chamber"}
        )
        session.add_all([scene1, scene2])
        session.flush()
        print(f"   ✓ Scene 1: {scene1.title} ({scene1.word_count} words)")
        print(f"   ✓ Scene 2: {scene2.title} ({scene2.word_count} words)")
        
        # Create Characters
        print("\n👤 Creating characters...")
        elara = Character(
            project_id=project.id,
            first_name="Elara",
            last_name="Windwhisper",
            nickname="The Apprentice",
            gender="Female",
            occupation="Mage Apprentice",
            physical_description="Tall and slender with long auburn hair and piercing green eyes",
            myers_briggs="INFJ",
            enneagram="Type 5 (The Investigator)",
            traits={"curious": 0.9, "brave": 0.6, "impulsive": 0.4, "loyal": 0.8},
            psychological_profile={
                "strengths": ["quick learner", "empathetic", "determined"],
                "weaknesses": ["self-doubt", "inexperienced"],
                "wounds": ["Abandoned as a child"]
            }
        )
        
        theron = Character(
            project_id=project.id,
            first_name="Theron",
            last_name="Stormweaver",
            title="Master",
            gender="Male",
            occupation="Archmage",
            physical_description="Ancient wizard with silver hair and weathered features",
            traits={"wise": 0.95, "patient": 0.7, "secretive": 0.8},
            psychological_profile={
                "strengths": ["vast knowledge", "mentorship"],
                "weaknesses": ["burdened by secrets"]
            }
        )
        session.add_all([elara, theron])
        session.flush()
        print(f"   ✓ {elara.first_name} {elara.last_name}")
        print(f"      - Traits: {elara.traits}")
        print(f"   ✓ {theron.title} {theron.first_name} {theron.last_name}")
        
        # Create Relationship
        print("\n🤝 Creating relationship...")
        relationship = Relationship(
            project_id=project.id,
            character_a_id=elara.id,
            character_b_id=theron.id,
            relationship_type="mentor-student",
            description="Theron has trained Elara for five years",
            attributes={"trust": 0.8, "respect": 0.9, "tension": 0.3},
            status="active",
            began_at="Five years ago"
        )
        session.add(relationship)
        print(f"   ✓ {relationship.relationship_type}: {elara.nickname} & {theron.title} {theron.last_name}")
        print(f"      - Dynamics: {relationship.attributes}")
        
        # Create Location
        print("\n🏰 Creating location...")
        tower = Location(
            project_id=project.id,
            name="The Ivory Tower",
            location_type="building",
            description="An ancient tower of white stone, home to the Order of Mages",
            atmosphere="Mysterious and scholarly",
            history="Built 1000 years ago by the founding mages",
            geography="Perched on a mountain peak",
            attributes={"magic_intensity": 0.9, "danger_level": 0.3, "isolation": 0.8},
            coordinates={"x": 1500, "y": 2300, "elevation": 3000}
        )
        session.add(tower)
        session.flush()
        print(f"   ✓ {tower.name}")
        print(f"      - Type: {tower.location_type}")
        print(f"      - Attributes: {tower.attributes}")
        
        # Create Event
        print("\n⚡ Creating event...")
        discovery = Event(
            project_id=project.id,
            title="Discovery of the Forbidden Tome",
            description="Elara finds an ancient book hidden in the tower's archives",
            event_type="discovery",
            occurred_at=datetime(2026, 1, 15, 14, 30),
            timeline_position=1,
            scope="personal",
            significance="This discovery will change everything",
            participants={"character_ids": [elara.id], "roles": {str(elara.id): "discoverer"}},
            locations={"location_ids": [tower.id], "primary_location_id": tower.id}
        )
        session.add(discovery)
        print(f"   ✓ {discovery.title}")
        print(f"      - Type: {discovery.event_type}")
        print(f"      - Participants: Character ID {elara.id} ({elara.nickname})")
        
        # Commit everything
        session.commit()
        print("\n" + "="*60)
        print("✅ All data committed successfully!")
        print("="*60)
        
    finally:
        session.close()
    
    # Now query and display the data
    print("\n\n" + "="*60)
    print("📊 EXPLORING THE DATABASE")
    print("="*60)
    
    session = db.SessionLocal()
    try:
        # Query project with all relationships
        project = session.query(Project).first()
        print(f"\n📚 PROJECT: {project.title}")
        print(f"   Author: {project.author}")
        print(f"   Meta: {project.meta}")
        
        print(f"\n   Stories ({len(project.stories)}):")
        for story in project.stories:
            print(f"   • {story.title}")
            print(f"     - Target: {story.word_count_target:,} words")
            print(f"     - Chapters: {len(story.chapters)}")
            
            for chapter in story.chapters:
                print(f"       └─ Ch{chapter.number}: {chapter.title} ({len(chapter.scenes)} scenes)")
                for scene in chapter.scenes:
                    print(f"          └─ {scene.title} ({scene.word_count} words)")
                    if scene.meta:
                        print(f"             POV: {scene.meta.get('pov')}, Setting: {scene.meta.get('setting')}")
        
        # Query characters
        characters = session.query(Character).all()
        print(f"\n👥 CHARACTERS ({len(characters)}):")
        for char in characters:
            name = f"{char.first_name} {char.last_name}"
            if char.nickname:
                name += f' "{char.nickname}"'
            print(f"   • {name}")
            print(f"     - {char.occupation}")
            if char.traits:
                print(f"     - Top traits: {', '.join(f'{k}={v}' for k, v in list(char.traits.items())[:3])}")
        
        # Query relationships
        relationships = session.query(Relationship).all()
        print(f"\n🤝 RELATIONSHIPS ({len(relationships)}):")
        for rel in relationships:
            print(f"   • {rel.relationship_type}")
            print(f"     - Status: {rel.status}")
            print(f"     - Dynamics: {rel.attributes}")
        
        # Query locations
        locations = session.query(Location).all()
        print(f"\n🏰 LOCATIONS ({len(locations)}):")
        for loc in locations:
            print(f"   • {loc.name} ({loc.location_type})")
            print(f"     - {loc.atmosphere}")
            if loc.attributes:
                print(f"     - Attributes: {loc.attributes}")
        
        # Query events
        events = session.query(Event).all()
        print(f"\n⚡ EVENTS ({len(events)}):")
        for event in events:
            print(f"   • {event.title}")
            print(f"     - Type: {event.event_type}")
            print(f"     - When: {event.occurred_at}")
            print(f"     - Significance: {event.significance}")
    
    finally:
        session.close()
    
    print("\n" + "="*60)
    print("✨ Database exploration complete!")
    print("="*60)


if __name__ == "__main__":
    main()
