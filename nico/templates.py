"""Story structure templates and generators."""
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum


class GenreType(Enum):
    """Story genre types."""
    ROMANCE = "romance"
    HERO_JOURNEY = "hero_journey"
    THRILLER = "thriller"
    MYSTERY = "mystery"
    THREE_ACT = "three_act"
    SAVE_THE_CAT = "save_the_cat"
    CUSTOM = "custom"


@dataclass
class SceneTemplate:
    """Template for a single scene."""
    title: str
    order: int
    beat: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    required_characters: List[str] = None
    location_hint: Optional[str] = None
    
    def __post_init__(self):
        if self.required_characters is None:
            self.required_characters = []


@dataclass
class ChapterTemplate:
    """Template for a chapter."""
    number: int
    title: str
    description: Optional[str] = None
    scenes: List[SceneTemplate] = None
    
    def __post_init__(self):
        if self.scenes is None:
            self.scenes = []


@dataclass
class StoryTemplate:
    """Complete story structure template."""
    name: str
    genre: GenreType
    description: str
    target_word_count: Optional[int]
    chapters: List[ChapterTemplate]
    character_archetypes: List[Dict[str, str]]  # [{"name": "Protagonist", "description": "..."}]
    location_suggestions: List[str]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class TemplateLibrary:
    """Library of predefined story templates."""
    
    @staticmethod
    def get_romance_novel_template() -> StoryTemplate:
        """
        Traditional romance novel structure (Romancing the Beat by Gwen Hayes).
        Approximately 80,000 words, 20-25 chapters.
        """
        chapters = [
            ChapterTemplate(
                number=1,
                title="The Setup",
                description="Introduce protagonist in their ordinary world",
                scenes=[
                    SceneTemplate(
                        title="Opening Scene",
                        order=1,
                        beat="Ordinary World",
                        description="Show protagonist's life before romance, establish desires/flaws",
                        notes="Hook the reader with character's voice and situation"
                    ),
                    SceneTemplate(
                        title="The Lack",
                        order=2,
                        beat="What's Missing",
                        description="Hint at what's missing from protagonist's life",
                        notes="Emotional wound or gap that love interest will fill"
                    )
                ]
            ),
            ChapterTemplate(
                number=2,
                title="The Meet-Cute",
                description="Protagonist meets love interest",
                scenes=[
                    SceneTemplate(
                        title="First Encounter",
                        order=1,
                        beat="The Meet-Cute",
                        description="Memorable first meeting between protagonist and love interest",
                        required_characters=["Protagonist", "Love Interest"],
                        notes="Should be memorable, possibly awkward or contentious"
                    ),
                    SceneTemplate(
                        title="First Impressions",
                        order=2,
                        beat="Initial Reaction",
                        description="Protagonist's thoughts about love interest after meeting",
                        notes="May be negative, intrigued, or conflicted"
                    )
                ]
            ),
            ChapterTemplate(
                number=3,
                title="The Refusal",
                description="Reasons they can't be together",
                scenes=[
                    SceneTemplate(
                        title="The Obstacle",
                        order=1,
                        beat="No Way",
                        description="Establish why relationship seems impossible",
                        notes="External obstacles or internal resistance"
                    )
                ]
            ),
            ChapterTemplate(
                number=4,
                title="The Connection",
                description="Forced proximity or circumstance brings them together",
                scenes=[
                    SceneTemplate(
                        title="Thrown Together",
                        order=1,
                        beat="Accept the Quest",
                        description="Circumstances force them to interact despite resistance",
                        required_characters=["Protagonist", "Love Interest"]
                    ),
                    SceneTemplate(
                        title="Glimpse of More",
                        order=2,
                        beat="Seeing Beneath",
                        description="First glimpse of love interest's deeper qualities",
                        notes="Show vulnerability or unexpected trait"
                    )
                ]
            ),
            ChapterTemplate(
                number=5,
                title="Building Attraction",
                description="Romantic tension increases",
                scenes=[
                    SceneTemplate(
                        title="Growing Closer",
                        order=1,
                        beat="Fun and Games",
                        description="Enjoyable interactions, banter, chemistry building",
                        required_characters=["Protagonist", "Love Interest"]
                    ),
                    SceneTemplate(
                        title="The Almost Kiss",
                        order=2,
                        beat="First Barrier Break",
                        description="Near-romantic moment that gets interrupted or pulled back from",
                        notes="Build sexual/romantic tension"
                    )
                ]
            ),
            ChapterTemplate(
                number=6,
                title="The First Kiss",
                description="First major romantic milestone",
                scenes=[
                    SceneTemplate(
                        title="The Kiss",
                        order=1,
                        beat="Midpoint/First Kiss",
                        description="The first kiss between protagonist and love interest",
                        required_characters=["Protagonist", "Love Interest"],
                        notes="Major turning point - no going back"
                    )
                ]
            ),
            ChapterTemplate(
                number=7,
                title="Falling in Love",
                description="Deepening relationship",
                scenes=[
                    SceneTemplate(
                        title="Bonding",
                        order=1,
                        beat="Falling",
                        description="Emotional intimacy deepens, sharing vulnerabilities",
                        required_characters=["Protagonist", "Love Interest"]
                    ),
                    SceneTemplate(
                        title="The High Point",
                        order=2,
                        beat="Peak Happiness",
                        description="Relationship at its best before complications arise",
                        notes="The 'all is well' moment"
                    )
                ]
            ),
            ChapterTemplate(
                number=8,
                title="The Crisis",
                description="Major conflict threatens the relationship",
                scenes=[
                    SceneTemplate(
                        title="The Reveal",
                        order=1,
                        beat="The Lurch",
                        description="Truth, secret, or misunderstanding comes to light",
                        notes="Turning point that threatens everything"
                    ),
                    SceneTemplate(
                        title="The Fight",
                        order=2,
                        beat="Dark Moment",
                        description="Confrontation between protagonist and love interest",
                        required_characters=["Protagonist", "Love Interest"],
                        notes="Emotional climax, things said that can't be unsaid"
                    )
                ]
            ),
            ChapterTemplate(
                number=9,
                title="The Separation",
                description="Relationship appears to be over",
                scenes=[
                    SceneTemplate(
                        title="The Break",
                        order=1,
                        beat="The Break-Up",
                        description="Protagonist and love interest part ways",
                        notes="Lowest emotional point"
                    ),
                    SceneTemplate(
                        title="Reflection",
                        order=2,
                        beat="Epiphany",
                        description="Protagonist realizes what they truly want/need",
                        notes="Character growth moment"
                    )
                ]
            ),
            ChapterTemplate(
                number=10,
                title="The Grand Gesture",
                description="Protagonist makes the choice",
                scenes=[
                    SceneTemplate(
                        title="The Decision",
                        order=1,
                        beat="Grand Gesture",
                        description="Protagonist takes action to win back love interest",
                        notes="Public declaration or significant sacrifice"
                    ),
                    SceneTemplate(
                        title="Happily Ever After",
                        order=2,
                        beat="Resolution/HEA",
                        description="Couple reunites, relationship solidified",
                        required_characters=["Protagonist", "Love Interest"],
                        notes="Satisfying emotional payoff"
                    )
                ]
            )
        ]
        
        return StoryTemplate(
            name="Classic Romance Novel",
            genre=GenreType.ROMANCE,
            description="Traditional romance structure with meet-cute, first kiss, dark moment, and HEA",
            target_word_count=80000,
            chapters=chapters,
            character_archetypes=[
                {
                    "name": "Protagonist",
                    "description": "Main character seeking love, with emotional wound or flaw to overcome"
                },
                {
                    "name": "Love Interest",
                    "description": "Romantic partner who challenges and complements protagonist"
                },
                {
                    "name": "Best Friend/Confidant",
                    "description": "Provides advice and support to protagonist"
                },
                {
                    "name": "Antagonist (optional)",
                    "description": "Ex-partner, rival, or other obstacle to the romance"
                }
            ],
            location_suggestions=[
                "Protagonist's Home",
                "Workplace/Meeting Ground",
                "Romantic Date Location",
                "Friend's Home",
                "Grand Gesture Location"
            ],
            metadata={
                "typical_length": "80,000 words",
                "chapters": "10",
                "source": "Romancing the Beat by Gwen Hayes"
            }
        )
    
    @staticmethod
    def get_heros_journey_template() -> StoryTemplate:
        """
        The Hero's Journey (Joseph Campbell's Monomyth).
        Epic adventure structure in 12 stages.
        """
        chapters = [
            ChapterTemplate(
                number=1,
                title="The Ordinary World",
                description="Hero in their normal life before the adventure",
                scenes=[
                    SceneTemplate(
                        title="Normal Life",
                        order=1,
                        beat="Ordinary World",
                        description="Establish hero's normal life, desires, and flaws",
                        required_characters=["Hero"]
                    )
                ]
            ),
            ChapterTemplate(
                number=2,
                title="The Call to Adventure",
                description="Hero receives challenge or quest",
                scenes=[
                    SceneTemplate(
                        title="The Call",
                        order=1,
                        beat="Call to Adventure",
                        description="Problem or quest is presented to hero",
                        required_characters=["Hero", "Herald"]
                    ),
                    SceneTemplate(
                        title="Refusal of the Call",
                        order=2,
                        beat="Refusal",
                        description="Hero hesitates or refuses the quest",
                        notes="Shows hero's fear or limitations"
                    )
                ]
            ),
            ChapterTemplate(
                number=3,
                title="Meeting the Mentor",
                description="Hero gains wisdom or tools for the journey",
                scenes=[
                    SceneTemplate(
                        title="The Mentor",
                        order=1,
                        beat="Meeting the Mentor",
                        description="Wise figure provides guidance, training, or magical item",
                        required_characters=["Hero", "Mentor"]
                    )
                ]
            ),
            ChapterTemplate(
                number=4,
                title="Crossing the Threshold",
                description="Hero leaves the ordinary world",
                scenes=[
                    SceneTemplate(
                        title="Point of No Return",
                        order=1,
                        beat="Crossing the Threshold",
                        description="Hero commits to the adventure and enters the special world",
                        required_characters=["Hero"],
                        notes="Major turning point - can't go back"
                    )
                ]
            ),
            ChapterTemplate(
                number=5,
                title="Tests, Allies, and Enemies",
                description="Hero learns the rules of the new world",
                scenes=[
                    SceneTemplate(
                        title="First Challenges",
                        order=1,
                        beat="Tests",
                        description="Hero faces initial challenges in the special world"
                    ),
                    SceneTemplate(
                        title="Gathering Allies",
                        order=2,
                        beat="Allies",
                        description="Hero forms bonds with companions",
                        notes="Introduce supporting cast"
                    ),
                    SceneTemplate(
                        title="Identifying Enemies",
                        order=3,
                        beat="Enemies",
                        description="Antagonistic forces reveal themselves"
                    )
                ]
            ),
            ChapterTemplate(
                number=6,
                title="Approach to the Inmost Cave",
                description="Hero prepares for major challenge",
                scenes=[
                    SceneTemplate(
                        title="Preparation",
                        order=1,
                        beat="Approach",
                        description="Hero and allies prepare for the main ordeal",
                        location_hint="Threshold to danger zone"
                    )
                ]
            ),
            ChapterTemplate(
                number=7,
                title="The Ordeal",
                description="Hero faces greatest fear or most difficult challenge",
                scenes=[
                    SceneTemplate(
                        title="The Crisis",
                        order=1,
                        beat="Ordeal",
                        description="Hero faces death or greatest fear",
                        required_characters=["Hero"],
                        notes="Climactic moment - hero may seem defeated"
                    )
                ]
            ),
            ChapterTemplate(
                number=8,
                title="The Reward",
                description="Hero survives and gains reward",
                scenes=[
                    SceneTemplate(
                        title="Seizing the Sword",
                        order=1,
                        beat="Reward",
                        description="Hero survives and takes possession of treasure/knowledge",
                        notes="May be physical object, knowledge, or reconciliation"
                    )
                ]
            ),
            ChapterTemplate(
                number=9,
                title="The Road Back",
                description="Hero begins return journey",
                scenes=[
                    SceneTemplate(
                        title="The Pursuit",
                        order=1,
                        beat="Road Back",
                        description="Hero begins return but faces final challenges",
                        notes="Consequences of ordeal catch up to hero"
                    )
                ]
            ),
            ChapterTemplate(
                number=10,
                title="Resurrection",
                description="Final test using all hero has learned",
                scenes=[
                    SceneTemplate(
                        title="Final Battle",
                        order=1,
                        beat="Resurrection",
                        description="Climactic confrontation where hero is tested one last time",
                        required_characters=["Hero"],
                        notes="Hero must prove transformation is complete"
                    )
                ]
            ),
            ChapterTemplate(
                number=11,
                title="Return with the Elixir",
                description="Hero returns transformed, bearing gift for others",
                scenes=[
                    SceneTemplate(
                        title="Homecoming",
                        order=1,
                        beat="Return",
                        description="Hero returns to ordinary world with treasure/wisdom",
                        required_characters=["Hero"],
                        location_hint="Original home/starting location"
                    ),
                    SceneTemplate(
                        title="The New Normal",
                        order=2,
                        beat="Elixir",
                        description="Hero's transformation benefits their community",
                        notes="Show how hero and world have changed"
                    )
                ]
            )
        ]
        
        return StoryTemplate(
            name="The Hero's Journey",
            genre=GenreType.HERO_JOURNEY,
            description="Classic monomyth structure: ordinary world → adventure → transformation → return",
            target_word_count=100000,
            chapters=chapters,
            character_archetypes=[
                {"name": "Hero", "description": "Protagonist who goes on the journey and transforms"},
                {"name": "Mentor", "description": "Wise guide who helps hero prepare"},
                {"name": "Herald", "description": "Brings the call to adventure"},
                {"name": "Threshold Guardian", "description": "Tests hero's commitment"},
                {"name": "Shapeshifter", "description": "Character whose loyalty is unclear"},
                {"name": "Shadow", "description": "Main antagonist or dark force"},
                {"name": "Ally/Trickster", "description": "Companion who provides support or comic relief"}
            ],
            location_suggestions=[
                "Ordinary World (Home)",
                "Threshold Crossing Point",
                "Special World",
                "Inmost Cave (Danger Zone)",
                "Return Location"
            ],
            metadata={
                "typical_length": "90,000-120,000 words",
                "chapters": "11-15",
                "source": "Joseph Campbell's Monomyth"
            }
        )
    
    @staticmethod
    def get_three_act_template() -> StoryTemplate:
        """Simple three-act structure."""
        chapters = [
            ChapterTemplate(
                number=1,
                title="Act I: Setup",
                description="Establish world, characters, and inciting incident",
                scenes=[
                    SceneTemplate(title="Opening Image", order=1, beat="Setup"),
                    SceneTemplate(title="Inciting Incident", order=2, beat="Catalyst"),
                ]
            ),
            ChapterTemplate(
                number=2,
                title="Act II: Confrontation",
                description="Rising action and obstacles",
                scenes=[
                    SceneTemplate(title="Escalating Conflict", order=1, beat="Rising Action"),
                    SceneTemplate(title="Midpoint", order=2, beat="Point of No Return"),
                    SceneTemplate(title="Dark Night", order=3, beat="All Is Lost"),
                ]
            ),
            ChapterTemplate(
                number=3,
                title="Act III: Resolution",
                description="Climax and denouement",
                scenes=[
                    SceneTemplate(title="Climax", order=1, beat="Final Confrontation"),
                    SceneTemplate(title="Resolution", order=2, beat="New Normal"),
                ]
            )
        ]
        
        return StoryTemplate(
            name="Three-Act Structure",
            genre=GenreType.THREE_ACT,
            description="Classic three-act structure: setup, confrontation, resolution",
            target_word_count=80000,
            chapters=chapters,
            character_archetypes=[
                {"name": "Protagonist", "description": "Main character with goal"},
                {"name": "Antagonist", "description": "Opposition to protagonist's goal"}
            ],
            location_suggestions=["Primary Setting", "Conflict Location", "Final Battle Location"],
            metadata={"typical_length": "60,000-100,000 words"}
        )
    
    @staticmethod
    def get_all_templates() -> List[StoryTemplate]:
        """Get all available templates."""
        return [
            TemplateLibrary.get_romance_novel_template(),
            TemplateLibrary.get_heros_journey_template(),
            TemplateLibrary.get_three_act_template(),
        ]
    
    @staticmethod
    def get_template_by_name(name: str) -> Optional[StoryTemplate]:
        """Get template by name."""
        templates = {t.name: t for t in TemplateLibrary.get_all_templates()}
        return templates.get(name)
