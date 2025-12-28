"""Use cases for Chapter operations."""

from typing import List, Optional
from uuid import UUID

from nico.domain.models import Chapter
from nico.domain.repositories import IChapterRepository
from nico.domain.services.ranking import generate_rank_key


class CreateChapterUseCase:
    """Create a new chapter in a story."""

    def __init__(self, chapter_repo: IChapterRepository):
        self.chapter_repo = chapter_repo

    def execute(
        self,
        story_id: UUID,
        title: str,
        synopsis: Optional[str] = None,
        status: str = "draft",
        after_chapter_id: Optional[UUID] = None,
    ) -> Chapter:
        """
        Create a new chapter.
        
        Args:
            story_id: Parent story ID
            title: Chapter title
            synopsis: Optional synopsis
            status: Chapter status (default: "draft")
            after_chapter_id: Optional ID of chapter to insert after (None = append to end)
            
        Returns:
            Created Chapter entity
        """
        chapters = self.chapter_repo.get_by_story(story_id)
        
        if not chapters:
            rank_key = generate_rank_key()
        elif after_chapter_id is None:
            last_rank = chapters[-1].rank_key
            rank_key = generate_rank_key(before=last_rank)
        else:
            after_idx = next((i for i, c in enumerate(chapters) if c.id == after_chapter_id), None)
            if after_idx is None:
                raise ValueError(f"Chapter {after_chapter_id} not found in story")
            
            before_rank = chapters[after_idx].rank_key
            after_rank = chapters[after_idx + 1].rank_key if after_idx + 1 < len(chapters) else None
            rank_key = generate_rank_key(before=before_rank, after=after_rank)

        chapter = Chapter(
            story_id=story_id,
            title=title,
            rank_key=rank_key,
            synopsis=synopsis,
            status=status,
        )

        return self.chapter_repo.create(chapter)


class ListChaptersUseCase:
    """List all chapters in a story."""

    def __init__(self, chapter_repo: IChapterRepository):
        self.chapter_repo = chapter_repo

    def execute(self, story_id: UUID) -> List[Chapter]:
        """
        List all chapters in a story, ordered by rank_key.
        
        Args:
            story_id: Story ID
            
        Returns:
            List of Chapter entities
        """
        return self.chapter_repo.get_by_story(story_id)


class UpdateChapterUseCase:
    """Update chapter metadata."""

    def __init__(self, chapter_repo: IChapterRepository):
        self.chapter_repo = chapter_repo

    def execute(
        self,
        chapter_id: UUID,
        title: Optional[str] = None,
        synopsis: Optional[str] = None,
        status: Optional[str] = None,
        exclude_from_ai: Optional[bool] = None,
    ) -> Chapter:
        """
        Update chapter metadata.
        
        Args:
            chapter_id: Chapter ID
            title: New title (optional)
            synopsis: New synopsis (optional)
            status: New status (optional)
            exclude_from_ai: New AI exclusion flag (optional)
            
        Returns:
            Updated Chapter entity
        """
        chapter = self.chapter_repo.get_by_id(chapter_id)
        if not chapter:
            raise ValueError(f"Chapter {chapter_id} not found")

        if title is not None:
            chapter.title = title
        if synopsis is not None:
            chapter.synopsis = synopsis
        if status is not None:
            chapter.status = status
        if exclude_from_ai is not None:
            chapter.exclude_from_ai = exclude_from_ai

        return self.chapter_repo.update(chapter)


class ReorderChapterUseCase:
    """Reorder a chapter within its story."""

    def __init__(self, chapter_repo: IChapterRepository):
        self.chapter_repo = chapter_repo

    def execute(self, chapter_id: UUID, after_chapter_id: Optional[UUID]) -> Chapter:
        """
        Move a chapter to a new position.
        
        Args:
            chapter_id: Chapter to move
            after_chapter_id: Chapter to insert after (None = move to beginning)
            
        Returns:
            Updated Chapter entity with new rank_key
        """
        chapter = self.chapter_repo.get_by_id(chapter_id)
        if not chapter:
            raise ValueError(f"Chapter {chapter_id} not found")

        chapters = self.chapter_repo.get_by_story(chapter.story_id)
        other_chapters = [c for c in chapters if c.id != chapter_id]

        if not other_chapters:
            return chapter

        if after_chapter_id is None:
            first_rank = other_chapters[0].rank_key
            chapter.rank_key = generate_rank_key(after=first_rank)
        else:
            after_idx = next((i for i, c in enumerate(other_chapters) if c.id == after_chapter_id), None)
            if after_idx is None:
                raise ValueError(f"Chapter {after_chapter_id} not found")
            
            before_rank = other_chapters[after_idx].rank_key
            after_rank = other_chapters[after_idx + 1].rank_key if after_idx + 1 < len(other_chapters) else None
            chapter.rank_key = generate_rank_key(before=before_rank, after=after_rank)

        return self.chapter_repo.update(chapter)


class DeleteChapterUseCase:
    """Delete a chapter and all its contents."""

    def __init__(self, chapter_repo: IChapterRepository):
        self.chapter_repo = chapter_repo

    def execute(self, chapter_id: UUID) -> None:
        """
        Delete a chapter.
        
        Args:
            chapter_id: Chapter ID
        """
        chapter = self.chapter_repo.get_by_id(chapter_id)
        if not chapter:
            raise ValueError(f"Chapter {chapter_id} not found")

        self.chapter_repo.delete(chapter_id)
