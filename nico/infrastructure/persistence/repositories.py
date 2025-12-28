"""SQLAlchemy repository implementations."""

import json
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from nico.domain.models import (
    Chapter,
    Character,
    CharacterTrait,
    Project,
    Scene,
    SceneDocument,
    SceneRevision,
    Story,
)
from nico.domain.repositories import (
    IChapterRepository,
    ICharacterRepository,
    IProjectRepository,
    ISceneDocumentRepository,
    ISceneRepository,
    IStoryRepository,
)
from nico.infrastructure.persistence.models import (
    ChapterModel,
    CharacterModel,
    CharacterTraitModel,
    ProjectModel,
    SceneDocumentModel,
    SceneModel,
    SceneRevisionModel,
    StoryModel,
)


class ProjectRepository(IProjectRepository):
    """SQLAlchemy implementation of project repository."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, project: Project) -> Project:
        """Create a new project."""
        model = ProjectModel(
            id=project.id,
            name=project.name,
            path=str(project.path),
            description=project.description,
            author=project.author,
            bibliography_style=project.bibliography_style,
            local_only_ai=project.local_only_ai,
            created_at=project.created_at,
            modified_at=project.modified_at,
        )
        self.session.add(model)
        self.session.commit()
        return project

    def get_by_id(self, project_id: UUID) -> Optional[Project]:
        """Get a project by ID."""
        model = self.session.query(ProjectModel).filter_by(id=project_id).first()
        return self._to_domain(model) if model else None

    def get_by_path(self, path: Path) -> Optional[Project]:
        """Get a project by its folder path."""
        model = self.session.query(ProjectModel).filter_by(path=str(path)).first()
        return self._to_domain(model) if model else None

    def update(self, project: Project) -> Project:
        """Update an existing project."""
        model = self.session.query(ProjectModel).filter_by(id=project.id).first()
        if not model:
            raise ValueError(f"Project {project.id} not found")

        model.name = project.name
        model.path = str(project.path)
        model.description = project.description
        model.author = project.author
        model.bibliography_style = project.bibliography_style
        model.local_only_ai = project.local_only_ai
        model.modified_at = project.modified_at

        self.session.commit()
        return project

    def delete(self, project_id: UUID) -> None:
        """Delete a project."""
        model = self.session.query(ProjectModel).filter_by(id=project_id).first()
        if model:
            self.session.delete(model)
            self.session.commit()

    @staticmethod
    def _to_domain(model: ProjectModel) -> Project:
        """Convert database model to domain entity."""
        return Project(
            id=model.id,
            name=model.name,
            path=Path(model.path),
            description=model.description,
            author=model.author,
            bibliography_style=model.bibliography_style,
            local_only_ai=model.local_only_ai,
            created_at=model.created_at,
            modified_at=model.modified_at,
        )


class StoryRepository(IStoryRepository):
    """SQLAlchemy implementation of story repository."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, story: Story) -> Story:
        """Create a new story."""
        model = StoryModel(
            id=story.id,
            project_id=story.project_id,
            title=story.title,
            rank_key=story.rank_key,
            synopsis=story.synopsis,
            status=story.status,
            exclude_from_ai=story.exclude_from_ai,
            created_at=story.created_at,
            modified_at=story.modified_at,
        )
        self.session.add(model)
        self.session.commit()
        return story

    def get_by_id(self, story_id: UUID) -> Optional[Story]:
        """Get a story by ID."""
        model = self.session.query(StoryModel).filter_by(id=story_id).first()
        return self._to_domain(model) if model else None

    def get_by_project(self, project_id: UUID) -> List[Story]:
        """Get all stories in a project, ordered by rank_key."""
        models = (
            self.session.query(StoryModel)
            .filter_by(project_id=project_id)
            .order_by(StoryModel.rank_key)
            .all()
        )
        return [self._to_domain(m) for m in models]

    def update(self, story: Story) -> Story:
        """Update an existing story."""
        model = self.session.query(StoryModel).filter_by(id=story.id).first()
        if not model:
            raise ValueError(f"Story {story.id} not found")

        model.title = story.title
        model.rank_key = story.rank_key
        model.synopsis = story.synopsis
        model.status = story.status
        model.exclude_from_ai = story.exclude_from_ai
        model.modified_at = story.modified_at

        self.session.commit()
        return story

    def delete(self, story_id: UUID) -> None:
        """Delete a story."""
        model = self.session.query(StoryModel).filter_by(id=story_id).first()
        if model:
            self.session.delete(model)
            self.session.commit()

    @staticmethod
    def _to_domain(model: StoryModel) -> Story:
        """Convert database model to domain entity."""
        return Story(
            id=model.id,
            project_id=model.project_id,
            title=model.title,
            rank_key=model.rank_key,
            synopsis=model.synopsis,
            status=model.status,
            exclude_from_ai=model.exclude_from_ai,
            created_at=model.created_at,
            modified_at=model.modified_at,
        )


class ChapterRepository(IChapterRepository):
    """SQLAlchemy implementation of chapter repository."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, chapter: Chapter) -> Chapter:
        """Create a new chapter."""
        model = ChapterModel(
            id=chapter.id,
            story_id=chapter.story_id,
            title=chapter.title,
            rank_key=chapter.rank_key,
            synopsis=chapter.synopsis,
            status=chapter.status,
            exclude_from_ai=chapter.exclude_from_ai,
            created_at=chapter.created_at,
            modified_at=chapter.modified_at,
        )
        self.session.add(model)
        self.session.commit()
        return chapter

    def get_by_id(self, chapter_id: UUID) -> Optional[Chapter]:
        """Get a chapter by ID."""
        model = self.session.query(ChapterModel).filter_by(id=chapter_id).first()
        return self._to_domain(model) if model else None

    def get_by_story(self, story_id: UUID) -> List[Chapter]:
        """Get all chapters in a story, ordered by rank_key."""
        models = (
            self.session.query(ChapterModel)
            .filter_by(story_id=story_id)
            .order_by(ChapterModel.rank_key)
            .all()
        )
        return [self._to_domain(m) for m in models]

    def update(self, chapter: Chapter) -> Chapter:
        """Update an existing chapter."""
        model = self.session.query(ChapterModel).filter_by(id=chapter.id).first()
        if not model:
            raise ValueError(f"Chapter {chapter.id} not found")

        model.title = chapter.title
        model.rank_key = chapter.rank_key
        model.synopsis = chapter.synopsis
        model.status = chapter.status
        model.exclude_from_ai = chapter.exclude_from_ai
        model.modified_at = chapter.modified_at

        self.session.commit()
        return chapter

    def delete(self, chapter_id: UUID) -> None:
        """Delete a chapter."""
        model = self.session.query(ChapterModel).filter_by(id=chapter_id).first()
        if model:
            self.session.delete(model)
            self.session.commit()

    @staticmethod
    def _to_domain(model: ChapterModel) -> Chapter:
        """Convert database model to domain entity."""
        return Chapter(
            id=model.id,
            story_id=model.story_id,
            title=model.title,
            rank_key=model.rank_key,
            synopsis=model.synopsis,
            status=model.status,
            exclude_from_ai=model.exclude_from_ai,
            created_at=model.created_at,
            modified_at=model.modified_at,
        )


class SceneRepository(ISceneRepository):
    """SQLAlchemy implementation of scene repository."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, scene: Scene) -> Scene:
        """Create a new scene."""
        model = SceneModel(
            id=scene.id,
            chapter_id=scene.chapter_id,
            title=scene.title,
            rank_key=scene.rank_key,
            synopsis=scene.synopsis,
            status=scene.status,
            pov_character_id=scene.pov_character_id,
            scene_date=scene.scene_date,
            word_count=scene.word_count,
            exclude_from_ai=scene.exclude_from_ai,
            created_at=scene.created_at,
            modified_at=scene.modified_at,
        )
        self.session.add(model)
        self.session.commit()
        return scene

    def get_by_id(self, scene_id: UUID) -> Optional[Scene]:
        """Get a scene by ID."""
        model = self.session.query(SceneModel).filter_by(id=scene_id).first()
        return self._to_domain(model) if model else None

    def get_by_chapter(self, chapter_id: UUID) -> List[Scene]:
        """Get all scenes in a chapter, ordered by rank_key."""
        models = (
            self.session.query(SceneModel)
            .filter_by(chapter_id=chapter_id)
            .order_by(SceneModel.rank_key)
            .all()
        )
        return [self._to_domain(m) for m in models]

    def update(self, scene: Scene) -> Scene:
        """Update an existing scene."""
        model = self.session.query(SceneModel).filter_by(id=scene.id).first()
        if not model:
            raise ValueError(f"Scene {scene.id} not found")

        model.title = scene.title
        model.rank_key = scene.rank_key
        model.synopsis = scene.synopsis
        model.status = scene.status
        model.pov_character_id = scene.pov_character_id
        model.scene_date = scene.scene_date
        model.word_count = scene.word_count
        model.exclude_from_ai = scene.exclude_from_ai
        model.modified_at = scene.modified_at

        self.session.commit()
        return scene

    def delete(self, scene_id: UUID) -> None:
        """Delete a scene."""
        model = self.session.query(SceneModel).filter_by(id=scene_id).first()
        if model:
            self.session.delete(model)
            self.session.commit()

    @staticmethod
    def _to_domain(model: SceneModel) -> Scene:
        """Convert database model to domain entity."""
        return Scene(
            id=model.id,
            chapter_id=model.chapter_id,
            title=model.title,
            rank_key=model.rank_key,
            synopsis=model.synopsis,
            status=model.status,
            pov_character_id=model.pov_character_id,
            scene_date=model.scene_date,
            word_count=model.word_count,
            exclude_from_ai=model.exclude_from_ai,
            created_at=model.created_at,
            modified_at=model.modified_at,
        )


class SceneDocumentRepository(ISceneDocumentRepository):
    """SQLAlchemy implementation of scene document repository."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, document: SceneDocument) -> SceneDocument:
        """Create a new scene document."""
        model = SceneDocumentModel(
            id=document.id,
            scene_id=document.scene_id,
            content=json.dumps(document.content),
            rendered_text=document.rendered_text,
            version=document.version,
            created_at=document.created_at,
            modified_at=document.modified_at,
        )
        self.session.add(model)
        self.session.commit()
        return document

    def get_by_scene_id(self, scene_id: UUID) -> Optional[SceneDocument]:
        """Get the document for a scene."""
        model = self.session.query(SceneDocumentModel).filter_by(scene_id=scene_id).first()
        return self._to_domain(model) if model else None

    def update(self, document: SceneDocument) -> SceneDocument:
        """Update an existing scene document."""
        model = self.session.query(SceneDocumentModel).filter_by(scene_id=document.scene_id).first()
        if not model:
            raise ValueError(f"SceneDocument for scene {document.scene_id} not found")

        model.content = json.dumps(document.content)
        model.rendered_text = document.rendered_text
        model.version = document.version
        model.modified_at = document.modified_at

        self.session.commit()
        return document

    def create_revision(self, revision: SceneRevision) -> SceneRevision:
        """Create a revision snapshot."""
        model = SceneRevisionModel(
            id=revision.id,
            scene_id=revision.scene_id,
            content=json.dumps(revision.content),
            rendered_text=revision.rendered_text,
            version=revision.version,
            reason=revision.reason,
            created_at=revision.created_at,
        )
        self.session.add(model)
        self.session.commit()
        return revision

    def get_revisions(self, scene_id: UUID, limit: Optional[int] = None) -> List[SceneRevision]:
        """Get revisions for a scene, most recent first."""
        query = (
            self.session.query(SceneRevisionModel)
            .filter_by(scene_id=scene_id)
            .order_by(SceneRevisionModel.created_at.desc())
        )
        if limit:
            query = query.limit(limit)
        models = query.all()
        return [self._revision_to_domain(m) for m in models]

    @staticmethod
    def _to_domain(model: SceneDocumentModel) -> SceneDocument:
        """Convert database model to domain entity."""
        return SceneDocument(
            id=model.id,
            scene_id=model.scene_id,
            content=json.loads(model.content),
            rendered_text=model.rendered_text,
            version=model.version,
            created_at=model.created_at,
            modified_at=model.modified_at,
        )

    @staticmethod
    def _revision_to_domain(model: SceneRevisionModel) -> SceneRevision:
        """Convert database model to domain entity."""
        return SceneRevision(
            id=model.id,
            scene_id=model.scene_id,
            content=json.loads(model.content),
            rendered_text=model.rendered_text,
            version=model.version,
            reason=model.reason,
            created_at=model.created_at,
        )


class CharacterRepository(ICharacterRepository):
    """SQLAlchemy implementation of character repository."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, character: Character) -> Character:
        """Create a new character."""
        model = CharacterModel(
            id=character.id,
            project_id=character.project_id,
            title=character.title,
            honorific=character.honorific,
            first_name=character.first_name,
            middle_name=character.middle_name,
            last_name=character.last_name,
            nickname=character.nickname,
            gender=character.gender,
            sex=character.sex,
            ethnicity=character.ethnicity,
            race=character.race,
            tribe_or_clan=character.tribe_or_clan,
            nationality=character.nationality,
            religion=character.religion,
            occupation=character.occupation,
            education=character.education,
            marital_status=character.marital_status,
            children=character.children,
            date_of_birth=character.date_of_birth,
            date_of_death=character.date_of_death,
            description=character.description,
            mbti=character.mbti,
            enneagram=character.enneagram,
            wounds=character.wounds,
            exclude_from_ai=character.exclude_from_ai,
            created_at=character.created_at,
            modified_at=character.modified_at,
        )
        self.session.add(model)
        self.session.commit()
        return character

    def get_by_id(self, character_id: UUID) -> Optional[Character]:
        """Get a character by ID."""
        model = self.session.query(CharacterModel).filter_by(id=character_id).first()
        return self._to_domain(model) if model else None

    def get_by_project(self, project_id: UUID) -> List[Character]:
        """Get all characters in a project."""
        models = self.session.query(CharacterModel).filter_by(project_id=project_id).all()
        return [self._to_domain(m) for m in models]

    def update(self, character: Character) -> Character:
        """Update an existing character."""
        model = self.session.query(CharacterModel).filter_by(id=character.id).first()
        if not model:
            raise ValueError(f"Character {character.id} not found")

        # Update all fields
        model.title = character.title
        model.honorific = character.honorific
        model.first_name = character.first_name
        model.middle_name = character.middle_name
        model.last_name = character.last_name
        model.nickname = character.nickname
        model.gender = character.gender
        model.sex = character.sex
        model.ethnicity = character.ethnicity
        model.race = character.race
        model.tribe_or_clan = character.tribe_or_clan
        model.nationality = character.nationality
        model.religion = character.religion
        model.occupation = character.occupation
        model.education = character.education
        model.marital_status = character.marital_status
        model.children = character.children
        model.date_of_birth = character.date_of_birth
        model.date_of_death = character.date_of_death
        model.description = character.description
        model.mbti = character.mbti
        model.enneagram = character.enneagram
        model.wounds = character.wounds
        model.exclude_from_ai = character.exclude_from_ai
        model.modified_at = character.modified_at

        self.session.commit()
        return character

    def delete(self, character_id: UUID) -> None:
        """Delete a character."""
        model = self.session.query(CharacterModel).filter_by(id=character_id).first()
        if model:
            self.session.delete(model)
            self.session.commit()

    def add_trait(self, trait: CharacterTrait) -> CharacterTrait:
        """Add a trait to a character."""
        model = CharacterTraitModel(
            id=trait.id,
            character_id=trait.character_id,
            name=trait.name,
            magnitude=trait.magnitude,
            position=trait.position,
            created_at=trait.created_at,
            modified_at=trait.modified_at,
        )
        self.session.add(model)
        self.session.commit()
        return trait

    def get_traits(self, character_id: UUID) -> List[CharacterTrait]:
        """Get all traits for a character, ordered by position."""
        models = (
            self.session.query(CharacterTraitModel)
            .filter_by(character_id=character_id)
            .order_by(CharacterTraitModel.position)
            .all()
        )
        return [self._trait_to_domain(m) for m in models]

    def update_trait(self, trait: CharacterTrait) -> CharacterTrait:
        """Update a character trait."""
        model = self.session.query(CharacterTraitModel).filter_by(id=trait.id).first()
        if not model:
            raise ValueError(f"CharacterTrait {trait.id} not found")

        model.name = trait.name
        model.magnitude = trait.magnitude
        model.position = trait.position
        model.modified_at = trait.modified_at

        self.session.commit()
        return trait

    def delete_trait(self, trait_id: UUID) -> None:
        """Delete a character trait."""
        model = self.session.query(CharacterTraitModel).filter_by(id=trait_id).first()
        if model:
            self.session.delete(model)
            self.session.commit()

    @staticmethod
    def _to_domain(model: CharacterModel) -> Character:
        """Convert database model to domain entity."""
        return Character(
            id=model.id,
            project_id=model.project_id,
            title=model.title,
            honorific=model.honorific,
            first_name=model.first_name,
            middle_name=model.middle_name,
            last_name=model.last_name,
            nickname=model.nickname,
            gender=model.gender,
            sex=model.sex,
            ethnicity=model.ethnicity,
            race=model.race,
            tribe_or_clan=model.tribe_or_clan,
            nationality=model.nationality,
            religion=model.religion,
            occupation=model.occupation,
            education=model.education,
            marital_status=model.marital_status,
            children=model.children,
            date_of_birth=model.date_of_birth,
            date_of_death=model.date_of_death,
            description=model.description,
            mbti=model.mbti,
            enneagram=model.enneagram,
            wounds=model.wounds,
            exclude_from_ai=model.exclude_from_ai,
            created_at=model.created_at,
            modified_at=model.modified_at,
        )

    @staticmethod
    def _trait_to_domain(model: CharacterTraitModel) -> CharacterTrait:
        """Convert database model to domain entity."""
        return CharacterTrait(
            id=model.id,
            character_id=model.character_id,
            name=model.name,
            magnitude=model.magnitude,
            position=model.position,
            created_at=model.created_at,
            modified_at=model.modified_at,
        )
