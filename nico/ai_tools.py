"""AI tool definitions for story generation.

These tool definitions allow an LLM to call story generation functions
to create structured stories from templates.
"""
from typing import List, Dict, Any, Optional
import json


# Tool definitions in OpenAI function calling format
STORY_GENERATOR_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_story_templates",
            "description": "List all available story structure templates. Returns templates like romance novels, hero's journey, three-act structure, etc.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_template_details",
            "description": "Get detailed information about a specific template including all chapters, scenes, beats, and character archetypes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "template_name": {
                        "type": "string",
                        "description": "Name of the template to get details for"
                    }
                },
                "required": ["template_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_story_from_template",
            "description": "Generate a complete story structure (chapters and scenes) from a template. Creates actual database records. Use this after discussing character names and preferences with the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "template_name": {
                        "type": "string",
                        "description": "Name of template to use (e.g., 'Classic Romance Novel', 'The Hero's Journey')"
                    },
                    "story_title": {
                        "type": "string",
                        "description": "Title for the generated story (optional, defaults to template name)"
                    },
                    "character_names": {
                        "type": "object",
                        "description": "Mapping of character archetypes to actual names (e.g., {'Protagonist': 'Emma', 'Love Interest': 'Liam'})",
                        "additionalProperties": {
                            "type": "string"
                        }
                    },
                    "location_names": {
                        "type": "object",
                        "description": "Mapping of location hints to actual place names",
                        "additionalProperties": {
                            "type": "string"
                        }
                    },
                    "skip_chapters": {
                        "type": "array",
                        "description": "List of chapter numbers to skip (optional)",
                        "items": {
                            "type": "integer"
                        }
                    }
                },
                "required": ["template_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_chapter_to_story",
            "description": "Add a single chapter from a template to an existing story. Use this to insert specific story beats or chapters.",
            "parameters": {
                "type": "object",
                "properties": {
                    "story_id": {
                        "type": "integer",
                        "description": "ID of the story to add chapter to"
                    },
                    "chapter_number": {
                        "type": "integer",
                        "description": "Chapter number (position in story)"
                    },
                    "chapter_title": {
                        "type": "string",
                        "description": "Title of the chapter"
                    },
                    "chapter_description": {
                        "type": "string",
                        "description": "Description of what happens in this chapter"
                    },
                    "scenes": {
                        "type": "array",
                        "description": "Array of scene definitions",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "order": {"type": "integer"},
                                "beat": {"type": "string"},
                                "description": {"type": "string"},
                                "required_characters": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "location_hint": {"type": "string"}
                            },
                            "required": ["title", "order"]
                        }
                    },
                    "insert_at": {
                        "type": "integer",
                        "description": "Position to insert chapter (optional, defaults to end)"
                    }
                },
                "required": ["story_id", "chapter_number", "chapter_title", "scenes"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_scene_to_chapter",
            "description": "Add a single scene to an existing chapter. Use this to insert specific story beats or scenes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "chapter_id": {
                        "type": "integer",
                        "description": "ID of the chapter to add scene to"
                    },
                    "scene_title": {
                        "type": "string",
                        "description": "Title of the scene"
                    },
                    "scene_order": {
                        "type": "integer",
                        "description": "Order/position of scene in chapter"
                    },
                    "beat": {
                        "type": "string",
                        "description": "Story beat this scene represents (optional)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of what happens in this scene"
                    },
                    "required_characters": {
                        "type": "array",
                        "description": "Character names that should appear in this scene",
                        "items": {"type": "string"}
                    },
                    "location_hint": {
                        "type": "string",
                        "description": "Location where scene takes place"
                    },
                    "notes": {
                        "type": "string",
                        "description": "Notes for the writer about this scene"
                    }
                },
                "required": ["chapter_id", "scene_title", "scene_order"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "preview_template_outline",
            "description": "Generate a preview outline of what a template would create, without actually creating database records. Use this to show the user what structure would be created.",
            "parameters": {
                "type": "object",
                "properties": {
                    "template_name": {
                        "type": "string",
                        "description": "Name of template to preview"
                    },
                    "character_names": {
                        "type": "object",
                        "description": "Character names to use in preview",
                        "additionalProperties": {
                            "type": "string"
                        }
                    }
                },
                "required": ["template_name"]
            }
        }
    }
]


class AIToolImplementations:
    """Implementations of AI tools for story generation."""
    
    def __init__(self, app_context):
        """
        Initialize with application context.
        
        Args:
            app_context: AppContext with story_generator service
        """
        self.app_context = app_context
    
    def list_story_templates(self) -> Dict[str, Any]:
        """List all available templates."""
        from nico.templates import TemplateLibrary
        
        templates = TemplateLibrary.get_all_templates()
        
        return {
            "templates": [
                {
                    "name": t.name,
                    "genre": t.genre.value,
                    "description": t.description,
                    "chapters": len(t.chapters),
                    "target_word_count": t.target_word_count,
                }
                for t in templates
            ]
        }
    
    def get_template_details(self, template_name: str) -> Dict[str, Any]:
        """Get detailed template information."""
        from nico.templates import TemplateLibrary
        
        template = TemplateLibrary.get_template_by_name(template_name)
        if not template:
            return {"error": f"Template not found: {template_name}"}
        
        return {
            "name": template.name,
            "genre": template.genre.value,
            "description": template.description,
            "target_word_count": template.target_word_count,
            "character_archetypes": template.character_archetypes,
            "location_suggestions": template.location_suggestions,
            "chapters": [
                {
                    "number": ch.number,
                    "title": ch.title,
                    "description": ch.description,
                    "scenes": [
                        {
                            "title": sc.title,
                            "order": sc.order,
                            "beat": sc.beat,
                            "description": sc.description,
                            "required_characters": sc.required_characters,
                            "location_hint": sc.location_hint,
                            "notes": sc.notes
                        }
                        for sc in ch.scenes
                    ]
                }
                for ch in template.chapters
            ]
        }
    
    def generate_story_from_template(
        self,
        project_id: int,
        template_name: str,
        story_title: Optional[str] = None,
        character_names: Optional[Dict[str, str]] = None,
        location_names: Optional[Dict[str, str]] = None,
        skip_chapters: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """Generate story from template."""
        from nico.templates import TemplateLibrary
        
        # Get template
        template = TemplateLibrary.get_template_by_name(template_name)
        if not template:
            return {"error": f"Template not found: {template_name}"}
        
        # Get project
        project = self.app_context.project_service.get_project(project_id)
        if not project:
            return {"error": f"Project not found: {project_id}"}
        
        # Build customization
        customization = {}
        if character_names:
            customization["character_names"] = character_names
        if location_names:
            customization["location_names"] = location_names
        if skip_chapters:
            customization["skip_chapters"] = skip_chapters
        
        # Generate story
        try:
            story = self.app_context.story_generator.generate_from_template(
                project=project,
                template=template,
                story_title=story_title,
                customization=customization
            )
            
            return {
                "success": True,
                "story_id": story.id,
                "story_title": story.title,
                "chapters_created": len(story.chapters),
                "total_scenes": sum(len(ch.scenes) for ch in story.chapters)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def add_chapter_to_story(
        self,
        story_id: int,
        chapter_number: int,
        chapter_title: str,
        chapter_description: str,
        scenes: List[Dict[str, Any]],
        insert_at: Optional[int] = None
    ) -> Dict[str, Any]:
        """Add chapter to existing story."""
        from nico.templates import ChapterTemplate, SceneTemplate
        
        # Get story through project
        projects = self.app_context.project_service.list_projects()
        story = None
        for project in projects:
            full_project = self.app_context.project_service.get_project(project.id)
            story = next((s for s in full_project.stories if s.id == story_id), None)
            if story:
                break
        
        if not story:
            return {"error": f"Story not found: {story_id}"}
        
        # Build chapter template
        scene_templates = [
            SceneTemplate(
                title=sc["title"],
                order=sc["order"],
                beat=sc.get("beat"),
                description=sc.get("description"),
                required_characters=sc.get("required_characters", []),
                location_hint=sc.get("location_hint")
            )
            for sc in scenes
        ]
        
        chapter_template = ChapterTemplate(
            number=chapter_number,
            title=chapter_title,
            description=chapter_description,
            scenes=scene_templates
        )
        
        try:
            chapter = self.app_context.story_generator.add_chapter_from_template(
                story=story,
                chapter_template=chapter_template,
                insert_at=insert_at
            )
            
            return {
                "success": True,
                "chapter_id": chapter.id,
                "chapter_number": chapter.number,
                "scenes_created": len(chapter.scenes)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def add_scene_to_chapter(
        self,
        chapter_id: int,
        scene_title: str,
        scene_order: int,
        beat: Optional[str] = None,
        description: Optional[str] = None,
        required_characters: Optional[List[str]] = None,
        location_hint: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add scene to existing chapter."""
        from nico.templates import SceneTemplate
        
        # Get chapter (through project hierarchy)
        projects = self.app_context.project_service.list_projects()
        chapter = None
        for project in projects:
            full_project = self.app_context.project_service.get_project(project.id)
            for story in full_project.stories:
                chapter = next((ch for ch in story.chapters if ch.id == chapter_id), None)
                if chapter:
                    break
            if chapter:
                break
        
        if not chapter:
            return {"error": f"Chapter not found: {chapter_id}"}
        
        # Build scene template
        scene_template = SceneTemplate(
            title=scene_title,
            order=scene_order,
            beat=beat,
            description=description,
            required_characters=required_characters or [],
            location_hint=location_hint,
            notes=notes
        )
        
        try:
            scene = self.app_context.story_generator.add_scene_from_template(
                chapter=chapter,
                scene_template=scene_template
            )
            
            return {
                "success": True,
                "scene_id": scene.id,
                "scene_title": scene.title
            }
        except Exception as e:
            return {"error": str(e)}
    
    def preview_template_outline(
        self,
        template_name: str,
        character_names: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Preview template outline without creating records."""
        from nico.templates import TemplateLibrary
        
        template = TemplateLibrary.get_template_by_name(template_name)
        if not template:
            return {"error": f"Template not found: {template_name}"}
        
        outline = self.app_context.story_generator.generate_outline_only(
            template=template,
            character_names=character_names
        )
        
        return outline
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool by name with arguments.
        
        This is the main entry point for AI systems to call tools.
        """
        if tool_name == "list_story_templates":
            return self.list_story_templates()
        elif tool_name == "get_template_details":
            return self.get_template_details(**arguments)
        elif tool_name == "generate_story_from_template":
            return self.generate_story_from_template(**arguments)
        elif tool_name == "add_chapter_to_story":
            return self.add_chapter_to_story(**arguments)
        elif tool_name == "add_scene_to_chapter":
            return self.add_scene_to_chapter(**arguments)
        elif tool_name == "preview_template_outline":
            return self.preview_template_outline(**arguments)
        else:
            return {"error": f"Unknown tool: {tool_name}"}
