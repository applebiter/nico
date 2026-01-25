"""Seed templates for immediate use - Mystery Thriller and Romance structures."""
from nico.domain.models import StoryTemplate, SceneTemplate, WorldBuildingTable
from nico.application.context import AppContext


def create_mystery_thriller_template(app_context: AppContext, project_id: int = None) -> StoryTemplate:
    """Create a Mystery Thriller story template.
    
    Based on classic detective/thriller structure with three acts,
    red herrings, escalating tension, and revelation.
    """
    template = StoryTemplate(
        project_id=project_id,  # None for global
        name="Mystery Thriller",
        genre="Mystery",
        description="Classic detective mystery with investigation, red herrings, and climactic revelation",
        target_word_count=75000,
        
        act_structure=[
            {
                "act": 1,
                "name": "Setup & Discovery",
                "chapters": [1, 6],
                "description": "Crime discovered, detective introduced, initial investigation begins"
            },
            {
                "act": 2,
                "name": "Investigation & Escalation",
                "chapters": [7, 18],
                "description": "Following leads, red herrings, stakes rise, second crime"
            },
            {
                "act": 3,
                "name": "Revelation & Resolution",
                "chapters": [19, 24],
                "description": "Truth uncovered, confrontation with culprit, justice served"
            }
        ],
        
        chapter_structure={
            "total_chapters": 24,
            "chapter_word_range": [2800, 3500],
            "chapter_templates": {
                "1": {
                    "type": "hook",
                    "required_elements": ["crime_scene", "victim_intro", "atmosphere"]
                },
                "6": {
                    "type": "first_turn",
                    "required_elements": ["false_lead", "detective_doubt"]
                },
                "12": {
                    "type": "midpoint",
                    "required_elements": ["second_crime", "pattern_emerges"]
                },
                "18": {
                    "type": "dark_moment",
                    "required_elements": ["all_seems_lost", "personal_stakes"]
                },
                "24": {
                    "type": "resolution",
                    "required_elements": ["justice", "closure", "reflection"]
                }
            }
        },
        
        required_beats=[
            {"name": "Crime Discovery", "position": 0.04, "description": "The crime that kicks off everything"},
            {"name": "Detective Enters", "position": 0.08, "description": "Protagonist takes the case"},
            {"name": "First Clue", "position": 0.15, "description": "Initial lead that seems promising"},
            {"name": "Red Herring", "position": 0.25, "description": "False accusation or misleading evidence"},
            {"name": "Second Crime", "position": 0.50, "description": "Pattern becomes clear, stakes raise"},
            {"name": "Personal Stakes", "position": 0.60, "description": "Detective or loved one threatened"},
            {"name": "Dark Night", "position": 0.75, "description": "All leads exhausted, seems unsolvable"},
            {"name": "Breakthrough", "position": 0.82, "description": "Key insight that unravels the mystery"},
            {"name": "Confrontation", "position": 0.90, "description": "Face-off with the culprit"},
            {"name": "Justice", "position": 0.96, "description": "Resolution and consequences"}
        ],
        
        required_scenes=[
            {"type": "crime_scene", "act": 1, "description": "Detailed examination of the crime scene"},
            {"type": "witness_interview", "act": 1, "description": "Questioning key witnesses"},
            {"type": "forensics", "act": 1, "description": "Evidence analysis"},
            {"type": "false_accusation", "act": 2, "description": "Wrong suspect confronted"},
            {"type": "chase", "act": 2, "description": "Physical pursuit or escape"},
            {"type": "revelation", "act": 3, "description": "Truth finally revealed"},
            {"type": "showdown", "act": 3, "description": "Final confrontation"},
        ],
        
        symbolic_themes=[
            "truth vs deception",
            "justice vs revenge",
            "guilt and redemption",
            "order vs chaos"
        ],
        
        is_public=True,
    )
    
    app_context._session.add(template)
    app_context._session.commit()
    
    return template


def create_romance_template(app_context: AppContext, project_id: int = None) -> StoryTemplate:
    """Create a Romance story template.
    
    Based on classic romance arc with meet-cute, conflict, and HEA/HFN.
    """
    template = StoryTemplate(
        project_id=project_id,
        name="Contemporary Romance",
        genre="Romance",
        description="Contemporary romance with emotional arc, conflict, and satisfying resolution",
        target_word_count=65000,
        
        act_structure=[
            {
                "act": 1,
                "name": "Meet & Attraction",
                "chapters": [1, 5],
                "description": "Meet-cute, initial attraction, external conflict introduced"
            },
            {
                "act": 2,
                "name": "Development & Conflict",
                "chapters": [6, 15],
                "description": "Relationship deepens, internal conflicts surface, obstacles arise"
            },
            {
                "act": 3,
                "name": "Crisis & Resolution",
                "chapters": [16, 20],
                "description": "Black moment, growth, reconciliation, HEA/HFN"
            }
        ],
        
        chapter_structure={
            "total_chapters": 20,
            "chapter_word_range": [3000, 3500],
            "chapter_templates": {
                "1": {
                    "type": "meet_cute",
                    "required_elements": ["first_impression", "spark", "obstacle_hint"]
                },
                "5": {
                    "type": "first_kiss",
                    "required_elements": ["chemistry", "tension", "interruption"]
                },
                "10": {
                    "type": "midpoint",
                    "required_elements": ["commitment", "vulnerability", "first_i_love_you"]
                },
                "15": {
                    "type": "dark_moment",
                    "required_elements": ["misunderstanding", "fear", "separation"]
                },
                "20": {
                    "type": "hea",
                    "required_elements": ["declaration", "commitment", "future"]
                }
            }
        },
        
        required_beats=[
            {"name": "Meet Cute", "position": 0.05, "description": "Memorable first encounter"},
            {"name": "Awareness", "position": 0.12, "description": "Recognize mutual attraction"},
            {"name": "First Kiss", "position": 0.25, "description": "Physical intimacy begins"},
            {"name": "Declaration", "position": 0.38, "description": "Emotional vulnerability"},
            {"name": "Commitment", "position": 0.50, "description": "Decide to try relationship"},
            {"name": "Conflict Surfaces", "position": 0.60, "description": "Internal/external obstacles"},
            {"name": "Black Moment", "position": 0.75, "description": "Relationship seems doomed"},
            {"name": "Realization", "position": 0.82, "description": "Understand what truly matters"},
            {"name": "Grand Gesture", "position": 0.90, "description": "Risk everything for love"},
            {"name": "HEA/HFN", "position": 0.98, "description": "Happily ever after or for now"}
        ],
        
        required_scenes=[
            {"type": "meet_cute", "act": 1, "description": "Charming or memorable first meeting"},
            {"type": "chemistry", "act": 1, "description": "Undeniable attraction moment"},
            {"type": "date", "act": 2, "description": "Getting to know each other"},
            {"type": "intimacy", "act": 2, "description": "Physical or emotional closeness"},
            {"type": "fight", "act": 2, "description": "Major argument or misunderstanding"},
            {"type": "separation", "act": 3, "description": "Time apart for reflection"},
            {"type": "reunion", "act": 3, "description": "Coming back together"},
        ],
        
        symbolic_themes=[
            "vulnerability vs protection",
            "independence vs partnership",
            "fear vs trust",
            "past wounds vs healing"
        ],
        
        is_public=True,
    )
    
    app_context._session.add(template)
    app_context._session.commit()
    
    return template


def create_scene_templates(app_context: AppContext, project_id: int = None) -> list[SceneTemplate]:
    """Create example scene templates with tag interpolation."""
    
    templates = []
    
    # Mystery scene templates
    templates.append(SceneTemplate(
        project_id=project_id,
        name="Crime Scene Discovery",
        scene_type="description",
        description="Detective arrives at crime scene and makes initial observations",
        template_text=(
            "{detective} arrived at the {location} just as {time_of_day}. "
            "The {weather} matched the grim scene inside. "
            "{victim_title} {victim_name} lay {position}, {cause_of_death}. "
            "The detective noticed {clue_1} near the body, and {clue_2} on the {surface}. "
            "Something about the {suspicious_detail} seemed off."
        ),
        table_mappings={
            "location": "locations.crime_scene",
            "time_of_day": "time.atmospheric",
            "weather": "weather.ominous",
            "victim_title": "titles.formal",
            "position": "positions.death",
            "cause_of_death": "death.causes",
            "clue_1": "clues.physical",
            "clue_2": "clues.overlooked",
            "surface": "furniture.common",
            "suspicious_detail": "details.suspicious"
        },
        example_output=(
            "Detective Morrison arrived at the abandoned warehouse just as dusk settled over the city. "
            "The gathering fog matched the grim scene inside. "
            "Dr. Eleanor Vance lay crumpled against the far wall, a single gunshot to the chest. "
            "The detective noticed fresh scratches near the body, and a torn business card on the concrete floor. "
            "Something about the unlocked door seemed off."
        ),
        is_public=True
    ))
    
    # Romance scene template
    templates.append(SceneTemplate(
        project_id=project_id,
        name="First Meeting",
        scene_type="dialogue",
        description="Two characters meet for the first time with chemistry",
        template_text=(
            "{protagonist} was {action} when {love_interest} {entrance}. "
            "Their eyes met, and {protagonist} felt {emotion}. "
            "\"{greeting},\" {love_interest} said, {vocal_quality}. "
            "{protagonist} noticed {attractive_feature} and {attractive_detail}. "
            "\"{response},\" {protagonist} managed, trying to sound {demeanor} despite {internal_reaction}."
        ),
        table_mappings={
            "action": "actions.mundane",
            "entrance": "entrances.memorable",
            "emotion": "emotions.attraction",
            "greeting": "dialogue.greeting",
            "vocal_quality": "voice.attractive",
            "attractive_feature": "appearance.striking",
            "attractive_detail": "appearance.subtle",
            "response": "dialogue.flustered",
            "demeanor": "demeanor.attempted",
            "internal_reaction": "reactions.internal"
        },
        example_output=(
            "Sarah was reorganizing the fiction section when the stranger pushed through the shop door, rainwater streaming from his jacket. "
            "Their eyes met, and Sarah felt her pulse quicken. "
            "\"Sorry for the mess,\" he said, with a self-deprecating smile. "
            "Sarah noticed his storm-gray eyes and the way his hair curled when wet. "
            "\"No worries, happens all the time,\" Sarah managed, trying to sound casual despite her suddenly dry mouth."
        ),
        is_public=True
    ))
    
    # Action scene template
    templates.append(SceneTemplate(
        project_id=project_id,
        name="Chase Sequence",
        scene_type="action",
        description="High-tension chase through environment",
        template_text=(
            "{protagonist} {chase_action} through the {location}, {obstacle_1} barely avoided. "
            "{pursuer} was {distance} behind, {weapon} in hand. "
            "{protagonist} {dodge_action}, using {environmental_feature} for cover. "
            "The {sound} of {pursuit_sound} echoed off the {surface}. "
            "Up ahead, {escape_route} offered a chance—if {protagonist} could reach it in time."
        ),
        table_mappings={
            "chase_action": "actions.movement",
            "location": "locations.urban",
            "obstacle_1": "obstacles.physical",
            "pursuer": "antagonist.types",
            "distance": "distance.close",
            "weapon": "weapons.handheld",
            "dodge_action": "actions.evasive",
            "environmental_feature": "environment.cover",
            "sound": "sounds.intensity",
            "pursuit_sound": "sounds.chase",
            "surface": "surfaces.urban",
            "escape_route": "exits.desperate"
        },
        is_public=True
    ))
    
    for template in templates:
        # Auto-extract tags
        template.required_tags = template.extract_tags()
        app_context._session.add(template)
    
    app_context._session.commit()
    
    return templates


def create_sample_world_building_tables(app_context: AppContext, project_id: int) -> list[WorldBuildingTable]:
    """Create sample world-building tables for the templates."""
    
    tables = []
    
    # Locations
    tables.append(WorldBuildingTable(
        project_id=project_id,
        table_name="locations.crime_scene",
        category="setting",
        description="Common crime scene locations",
        items=[
            "abandoned warehouse",
            "luxury penthouse",
            "dimly lit alley",
            "suburban home",
            "downtown office",
            "parking garage",
            "waterfront pier",
            "hotel suite"
        ]
    ))
    
    # Weather
    tables.append(WorldBuildingTable(
        project_id=project_id,
        table_name="weather.ominous",
        category="atmosphere",
        description="Weather that enhances mood",
        items=[
            "gathering fog",
            "steady rain",
            "oppressive humidity",
            "unseasonable cold",
            "bruised storm clouds",
            "bone-chilling wind"
        ]
    ))
    
    # Clues
    tables.append(WorldBuildingTable(
        project_id=project_id,
        table_name="clues.physical",
        category="plot",
        description="Physical evidence",
        items=[
            "fresh scratches",
            "muddy footprints",
            "torn fabric",
            "broken glass",
            "smudged fingerprints",
            "cigarette butts",
            "dried blood",
            "a single earring"
        ]
    ))
    
    # Suspicious details
    tables.append(WorldBuildingTable(
        project_id=project_id,
        table_name="details.suspicious",
        category="plot",
        description="Things that seem off",
        items=[
            "unlocked door",
            "missing photographs",
            "recently wiped surfaces",
            "muddy tracks leading away",
            "out-of-place furniture",
            "disconnected security camera",
            "missing wallet",
            "strange smell"
        ]
    ))
    
    # Emotions - Attraction
    tables.append(WorldBuildingTable(
        project_id=project_id,
        table_name="emotions.attraction",
        category="character",
        description="Initial attraction feelings",
        items=[
            "her pulse quicken",
            "butterflies in her stomach",
            "heat rise to her cheeks",
            "her breath catch",
            "electricity down her spine",
            "her thoughts scatter"
        ]
    ))
    
    # Appearance
    tables.append(WorldBuildingTable(
        project_id=project_id,
        table_name="appearance.striking",
        category="character",
        description="Noticeable physical features",
        items=[
            "storm-gray eyes",
            "a crooked smile",
            "dimples when he laughed",
            "strong jawline",
            "elegant hands",
            "athletic build"
        ]
    ))
    
    for table in tables:
        app_context._session.add(table)
    
    app_context._session.commit()
    
    return tables


def seed_all_templates(app_context: AppContext, project_id: int = None) -> dict:
    """Seed all example templates and tables.
    
    Args:
        app_context: Application context
        project_id: Optional project ID (None for global templates)
        
    Returns:
        Dict with created objects
    """
    print("Creating story templates...")
    mystery_template = create_mystery_thriller_template(app_context, project_id)
    romance_template = create_romance_template(app_context, project_id)
    
    print("Creating scene templates...")
    scene_templates = create_scene_templates(app_context, project_id)
    
    result = {
        "story_templates": [mystery_template, romance_template],
        "scene_templates": scene_templates,
    }
    
    # Only create sample tables if project_id specified
    if project_id:
        print(f"Creating sample world-building tables for project {project_id}...")
        tables = create_sample_world_building_tables(app_context, project_id)
        result["world_building_tables"] = tables
    
    print(f"\nSeeded successfully:")
    print(f"  - {len(result['story_templates'])} story templates")
    print(f"  - {len(result['scene_templates'])} scene templates")
    if "world_building_tables" in result:
        print(f"  - {len(result['world_building_tables'])} world-building tables")
    
    return result
