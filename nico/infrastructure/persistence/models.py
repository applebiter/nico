"""SQLAlchemy database models for persistence."""

from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


def uuid_pk() -> UUID:
    """Generate a UUID for primary keys."""
    return uuid4()


class ProjectModel(Base):
    """SQLAlchemy model for Project."""

    __tablename__ = "projects"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid_pk)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    path: Mapped[str] = mapped_column(String(1024), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    author: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    bibliography_style: Mapped[str] = mapped_column(String(50), nullable=False, default="MLA")
    local_only_ai: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    modified_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    stories: Mapped[list["StoryModel"]] = relationship(
        "StoryModel", back_populates="project", cascade="all, delete-orphan"
    )
    characters: Mapped[list["CharacterModel"]] = relationship(
        "CharacterModel", back_populates="project", cascade="all, delete-orphan"
    )


class StoryModel(Base):
    """SQLAlchemy model for Story."""

    __tablename__ = "stories"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid_pk)
    project_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    rank_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    synopsis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    exclude_from_ai: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    modified_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    project: Mapped["ProjectModel"] = relationship("ProjectModel", back_populates="stories")
    chapters: Mapped[list["ChapterModel"]] = relationship(
        "ChapterModel", back_populates="story", cascade="all, delete-orphan"
    )


class ChapterModel(Base):
    """SQLAlchemy model for Chapter."""

    __tablename__ = "chapters"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid_pk)
    story_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("stories.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    rank_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    synopsis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    exclude_from_ai: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    modified_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    story: Mapped["StoryModel"] = relationship("StoryModel", back_populates="chapters")
    scenes: Mapped[list["SceneModel"]] = relationship(
        "SceneModel", back_populates="chapter", cascade="all, delete-orphan"
    )


class SceneModel(Base):
    """SQLAlchemy model for Scene."""

    __tablename__ = "scenes"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid_pk)
    chapter_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("chapters.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    rank_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    synopsis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    pov_character_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("characters.id"), nullable=True
    )
    scene_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    word_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    exclude_from_ai: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    modified_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    chapter: Mapped["ChapterModel"] = relationship("ChapterModel", back_populates="scenes")
    pov_character: Mapped[Optional["CharacterModel"]] = relationship("CharacterModel")
    document: Mapped[Optional["SceneDocumentModel"]] = relationship(
        "SceneDocumentModel", back_populates="scene", uselist=False, cascade="all, delete-orphan"
    )
    revisions: Mapped[list["SceneRevisionModel"]] = relationship(
        "SceneRevisionModel", back_populates="scene", cascade="all, delete-orphan"
    )


class SceneDocumentModel(Base):
    """SQLAlchemy model for SceneDocument."""

    __tablename__ = "scene_documents"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid_pk)
    scene_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("scenes.id"), nullable=False, unique=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)  # JSON as text
    rendered_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    modified_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    scene: Mapped["SceneModel"] = relationship("SceneModel", back_populates="document")


class SceneRevisionModel(Base):
    """SQLAlchemy model for SceneRevision."""

    __tablename__ = "scene_revisions"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid_pk)
    scene_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("scenes.id"), nullable=False, index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)  # JSON as text
    rendered_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    scene: Mapped["SceneModel"] = relationship("SceneModel", back_populates="revisions")


class CharacterModel(Base):
    """SQLAlchemy model for Character."""

    __tablename__ = "characters"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid_pk)
    project_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    
    # Identity & naming
    title: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    honorific: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    middle_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    nickname: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Demographics
    gender: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    sex: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    ethnicity: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    race: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tribe_or_clan: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    nationality: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    religion: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Life & social
    occupation: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    education: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    marital_status: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    children: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Dates
    date_of_birth: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    date_of_death: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    
    # Descriptive/psychological
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    mbti: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    enneagram: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    wounds: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Metadata
    exclude_from_ai: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    modified_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    project: Mapped["ProjectModel"] = relationship("ProjectModel", back_populates="characters")
    traits: Mapped[list["CharacterTraitModel"]] = relationship(
        "CharacterTraitModel", back_populates="character", cascade="all, delete-orphan"
    )


class CharacterTraitModel(Base):
    """SQLAlchemy model for CharacterTrait."""

    __tablename__ = "character_traits"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid_pk)
    character_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("characters.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    magnitude: Mapped[int] = mapped_column(Integer, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    modified_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    character: Mapped["CharacterModel"] = relationship("CharacterModel", back_populates="traits")
