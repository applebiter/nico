"""Character domain model."""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from .base import Entity


class Character(Entity):
    """
    Project-wide character entity with comprehensive attributes.
    
    Characters are absolute-aware: base fields represent canonical facts,
    while time-ranged facts (relationships, occupation changes) are modeled separately.
    """

    def __init__(
        self,
        project_id: UUID,
        id: Optional[UUID] = None,
        # Identity & naming
        title: Optional[str] = None,
        honorific: Optional[str] = None,
        first_name: Optional[str] = None,
        middle_name: Optional[str] = None,
        last_name: Optional[str] = None,
        nickname: Optional[str] = None,
        # Demographics
        gender: Optional[str] = None,
        sex: Optional[str] = None,
        ethnicity: Optional[str] = None,
        race: Optional[str] = None,
        tribe_or_clan: Optional[str] = None,
        nationality: Optional[str] = None,
        religion: Optional[str] = None,
        # Life & social
        occupation: Optional[str] = None,
        education: Optional[str] = None,
        marital_status: Optional[str] = None,
        children: Optional[str] = None,
        # Dates
        date_of_birth: Optional[date] = None,
        date_of_death: Optional[date] = None,
        # Descriptive/psychological
        description: Optional[str] = None,
        mbti: Optional[str] = None,
        enneagram: Optional[str] = None,
        wounds: Optional[str] = None,
        # Metadata
        exclude_from_ai: bool = False,
        created_at: Optional[datetime] = None,
        modified_at: Optional[datetime] = None,
    ):
        super().__init__(id)
        self.project_id = project_id
        
        # Identity & naming
        self.title = title
        self.honorific = honorific
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.nickname = nickname
        
        # Demographics
        self.gender = gender
        self.sex = sex
        self.ethnicity = ethnicity
        self.race = race
        self.tribe_or_clan = tribe_or_clan
        self.nationality = nationality
        self.religion = religion
        
        # Life & social
        self.occupation = occupation
        self.education = education
        self.marital_status = marital_status
        self.children = children
        
        # Dates
        self.date_of_birth = date_of_birth
        self.date_of_death = date_of_death
        
        # Descriptive/psychological
        self.description = description
        self.mbti = mbti
        self.enneagram = enneagram
        self.wounds = wounds
        
        # Metadata
        self.exclude_from_ai = exclude_from_ai
        
        if created_at:
            self.created_at = created_at
        if modified_at:
            self.modified_at = modified_at

    @property
    def full_name(self) -> str:
        """Compute full name from components."""
        parts = []
        if self.honorific:
            parts.append(self.honorific)
        if self.first_name:
            parts.append(self.first_name)
        if self.middle_name:
            parts.append(self.middle_name)
        if self.last_name:
            parts.append(self.last_name)
        if self.nickname:
            parts.append(f'"{self.nickname}"')
        return " ".join(parts) if parts else "Unnamed Character"

    @property
    def age(self) -> Optional[int]:
        """Calculate age from date_of_birth (and date_of_death if applicable)."""
        if not self.date_of_birth:
            return None
        
        end_date = self.date_of_death or date.today()
        age = end_date.year - self.date_of_birth.year
        
        # Adjust if birthday hasn't occurred yet this year
        if (end_date.month, end_date.day) < (self.date_of_birth.month, self.date_of_birth.day):
            age -= 1
        
        return age

    def __repr__(self) -> str:
        return f"<Character(id={self.id}, name='{self.full_name}')>"


class CharacterTrait(Entity):
    """
    A trait associated with a Character, with ordering and magnitude.
    
    Traits have:
    - position: ordering within the character's trait list
    - name: trait descriptor (e.g., "neuroticism", "bravery", "intelligence")
    - magnitude: 0-100 scale indicating intensity
    """

    def __init__(
        self,
        character_id: UUID,
        name: str,
        magnitude: int,
        position: int,
        id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        modified_at: Optional[datetime] = None,
    ):
        super().__init__(id)
        self.character_id = character_id
        self.name = name
        self.magnitude = self._validate_magnitude(magnitude)
        self.position = position
        
        if created_at:
            self.created_at = created_at
        if modified_at:
            self.modified_at = modified_at

    @staticmethod
    def _validate_magnitude(magnitude: int) -> int:
        """Ensure magnitude is within 0-100 range."""
        if magnitude < 0:
            return 0
        if magnitude > 100:
            return 100
        return magnitude

    def __repr__(self) -> str:
        return f"<CharacterTrait(name='{self.name}', magnitude={self.magnitude}, position={self.position})>"
