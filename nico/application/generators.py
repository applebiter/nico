"""Story generation services that create database entities from templates."""
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from nico.domain.models.project import Project
from nico.domain.models.story import Story
from nico.domain.models.chapter import Chapter
from nico.domain.models.scene import Scene
from nico.templates import StoryTemplate, ChapterTemplate, SceneTemplate


class StoryGenerator:
    """Generates story structures from templates."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def generate_from_template(
        self,
        project: Project,
        template: StoryTemplate,
        story_title: Optional[str] = None,
        customization: Optional[Dict[str, Any]] = None
    ) -> Story:
        """
        Generate a complete story structure from a template.
        
        Args:
            project: Project to add story to
            template: Story template to use
            story_title: Override template name with custom title
            customization: Optional dict with customizations:
                - character_names: dict mapping archetype names to actual names
                - location_names: dict mapping location hints to actual names
                - skip_chapters: list of chapter numbers to skip
                - merge_chapters: list of tuples (ch1, ch2) to merge
        
        Returns:
            Generated Story object with all chapters and scenes
        """
        customization = customization or {}
        
        # Create the story
        story = Story(
            title=story_title or template.name,
            description=template.description,
            project_id=project.id,
            order=len(project.stories or []),
            metadata={
                "generated_from_template": template.name,
                "genre": template.genre.value,
                "target_word_count": template.target_word_count,
                "character_archetypes": template.character_archetypes,
                "location_suggestions": template.location_suggestions,
            }
        )
        self.session.add(story)
        self.session.flush()  # Get story.id
        
        # Get customization options
        character_names = customization.get("character_names", {})
        location_names = customization.get("location_names", {})
        skip_chapters = set(customization.get("skip_chapters", []))
        
        # Generate chapters
        for chapter_template in template.chapters:
            if chapter_template.number in skip_chapters:
                continue
            
            self._generate_chapter(
                story=story,
                chapter_template=chapter_template,
                character_names=character_names,
                location_names=location_names
            )
        
        self.session.commit()
        return story
    
    def _generate_chapter(
        self,
        story: Story,
        chapter_template: ChapterTemplate,
        character_names: Dict[str, str],
        location_names: Dict[str, str]
    ) -> Chapter:
        """Generate a chapter from template."""
        # Create chapter
        chapter = Chapter(
            number=chapter_template.number,
            title=chapter_template.title,
            description=chapter_template.description,
            story_id=story.id,
            metadata={"generated_from_template": True}
        )
        self.session.add(chapter)
        self.session.flush()  # Get chapter.id
        
        # Generate scenes
        for scene_template in chapter_template.scenes:
            self._generate_scene(
                chapter=chapter,
                scene_template=scene_template,
                character_names=character_names,
                location_names=location_names
            )
        
        return chapter
    
    def _generate_scene(
        self,
        chapter: Chapter,
        scene_template: SceneTemplate,
        character_names: Dict[str, str],
        location_names: Dict[str, str]
    ) -> Scene:
        """Generate a scene from template."""
        # Build scene content with placeholder guidance
        content_parts = []
        
        if scene_template.beat:
            content_parts.append(f"[BEAT: {scene_template.beat}]")
        
        if scene_template.description:
            content_parts.append(f"\n\n{scene_template.description}")
        
        if scene_template.required_characters:
            char_list = []
            for archetype in scene_template.required_characters:
                actual_name = character_names.get(archetype, f"[{archetype}]")
                char_list.append(actual_name)
            content_parts.append(f"\n\nRequired Characters: {', '.join(char_list)}")
        
        if scene_template.location_hint:
            location = location_names.get(
                scene_template.location_hint,
                f"[{scene_template.location_hint}]"
            )
            content_parts.append(f"\nLocation: {location}")
        
        if scene_template.notes:
            content_parts.append(f"\n\nNotes for Writer:\n{scene_template.notes}")
        
        content_parts.append("\n\n[Write scene here...]")
        
        # Create scene
        scene = Scene(
            title=scene_template.title,
            content="".join(content_parts),
            order=scene_template.order,
            chapter_id=chapter.id,
            metadata={
                "generated_from_template": True,
                "beat": scene_template.beat,
                "template_description": scene_template.description,
                "required_characters": scene_template.required_characters,
                "location_hint": scene_template.location_hint,
            }
        )
        self.session.add(scene)
        
        return scene
    
    def add_chapter_from_template(
        self,
        story: Story,
        chapter_template: ChapterTemplate,
        insert_at: Optional[int] = None,
        character_names: Optional[Dict[str, str]] = None,
        location_names: Optional[Dict[str, str]] = None
    ) -> Chapter:
        """
        Add a single chapter to existing story from template.
        
        Useful for AI tools to insert specific beats or chapters.
        """
        character_names = character_names or {}
        location_names = location_names or {}
        
        # Adjust chapter number if inserting
        if insert_at is not None:
            # Renumber subsequent chapters
            for chapter in story.chapters:
                if chapter.number >= insert_at:
                    chapter.number += 1
            chapter_template.number = insert_at
        else:
            # Add at end
            chapter_template.number = len(story.chapters) + 1
        
        chapter = self._generate_chapter(
            story=story,
            chapter_template=chapter_template,
            character_names=character_names,
            location_names=location_names
        )
        
        self.session.commit()
        return chapter
    
    def add_scene_from_template(
        self,
        chapter: Chapter,
        scene_template: SceneTemplate,
        insert_at: Optional[int] = None,
        character_names: Optional[Dict[str, str]] = None,
        location_names: Optional[Dict[str, str]] = None
    ) -> Scene:
        """
        Add a single scene to existing chapter from template.
        
        Useful for AI tools to insert specific beats or scenes.
        """
        character_names = character_names or {}
        location_names = location_names or {}
        
        # Adjust scene order if inserting
        if insert_at is not None:
            for scene in chapter.scenes:
                if scene.order >= insert_at:
                    scene.order += 1
            scene_template.order = insert_at
        else:
            # Add at end
            max_order = max([s.order for s in chapter.scenes], default=0)
            scene_template.order = max_order + 1
        
        scene = self._generate_scene(
            chapter=chapter,
            scene_template=scene_template,
            character_names=character_names,
            location_names=location_names
        )
        
        self.session.commit()
        return scene
    
    def generate_outline_only(
        self,
        template: StoryTemplate,
        character_names: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Generate an outline without creating database entities.
        
        Useful for preview or AI planning.
        
        Returns:
            Dict with structure: {
                "title": str,
                "description": str,
                "chapters": [{"number": int, "title": str, "scenes": [...]}]
            }
        """
        character_names = character_names or {}
        
        outline = {
            "title": template.name,
            "description": template.description,
            "genre": template.genre.value,
            "target_word_count": template.target_word_count,
            "chapters": []
        }
        
        for chapter_template in template.chapters:
            chapter_outline = {
                "number": chapter_template.number,
                "title": chapter_template.title,
                "description": chapter_template.description,
                "scenes": []
            }
            
            for scene_template in chapter_template.scenes:
                # Map character archetypes to names
                characters = [
                    character_names.get(arch, arch)
                    for arch in (scene_template.required_characters or [])
                ]
                
                scene_outline = {
                    "title": scene_template.title,
                    "order": scene_template.order,
                    "beat": scene_template.beat,
                    "description": scene_template.description,
                    "characters": characters,
                    "location": scene_template.location_hint,
                }
                chapter_outline["scenes"].append(scene_outline)
            
            outline["chapters"].append(chapter_outline)
        
        return outline


class TemplateCustomizer:
    """Helper for customizing templates with user input."""
    
    @staticmethod
    def customize_romance_template(
        protagonist_name: str,
        love_interest_name: str,
        setting: str = "Contemporary",
        occupation_protagonist: Optional[str] = None,
        occupation_love_interest: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create customization dict for romance template.
        
        Args:
            protagonist_name: Name of main character
            love_interest_name: Name of romantic partner
            setting: Time period/setting type
            occupation_protagonist: Job/role of protagonist
            occupation_love_interest: Job/role of love interest
        
        Returns:
            Customization dict for use with StoryGenerator
        """
        character_names = {
            "Protagonist": protagonist_name,
            "Love Interest": love_interest_name,
            "Best Friend/Confidant": f"{protagonist_name}'s friend",
        }
        
        # Suggest locations based on setting
        if setting.lower() == "contemporary":
            location_names = {
                "Protagonist's Home": f"{protagonist_name}'s apartment",
                "Workplace/Meeting Ground": "Coffee shop" if not occupation_protagonist else f"{occupation_protagonist} office",
                "Romantic Date Location": "Rooftop restaurant",
                "Grand Gesture Location": "City plaza",
            }
        elif setting.lower() == "historical":
            location_names = {
                "Protagonist's Home": f"{protagonist_name}'s estate",
                "Workplace/Meeting Ground": "Grand ballroom",
                "Romantic Date Location": "Garden promenade",
                "Grand Gesture Location": "Society ball",
            }
        else:
            location_names = {}
        
        return {
            "character_names": character_names,
            "location_names": location_names,
        }
    
    @staticmethod
    def customize_heros_journey(
        hero_name: str,
        mentor_name: Optional[str] = None,
        villain_name: Optional[str] = None,
        quest_object: str = "the ancient artifact"
    ) -> Dict[str, Any]:
        """Create customization dict for hero's journey template."""
        character_names = {
            "Hero": hero_name,
            "Mentor": mentor_name or "the wise mentor",
            "Shadow": villain_name or "the dark lord",
            "Herald": "the messenger",
            "Threshold Guardian": "the guardian",
        }
        
        location_names = {
            "Ordinary World (Home)": f"{hero_name}'s village",
            "Threshold Crossing Point": "The great gate",
            "Special World": "The realm of shadow",
            "Inmost Cave (Danger Zone)": "The dark fortress",
            "Return Location": f"{hero_name}'s village",
        }
        
        return {
            "character_names": character_names,
            "location_names": location_names,
        }
