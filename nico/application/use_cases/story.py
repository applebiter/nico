"""Use cases for Story operations."""

from typing import List, Optional
from uuid import UUID

from nico.domain.models import Story
from nico.domain.repositories import IStoryRepository
from nico.domain.services.ranking import generate_rank_key


class CreateStoryUseCase:
    """Create a new story in a project."""

    def __init__(self, story_repo: IStoryRepository):
        self.story_repo = story_repo

    def execute(
        self,
        project_id: UUID,
        title: str,
        synopsis: Optional[str] = None,
        status: str = "draft",
        after_story_id: Optional[UUID] = None,
    ) -> Story:
        """
        Create a new story.
        
        Args:
            project_id: Parent project ID
            title: Story title
            synopsis: Optional synopsis
            status: Story status (default: "draft")
            after_story_id: Optional ID of story to insert after (None = append to end)
            
        Returns:
            Created Story entity
        """
        # Get existing stories to determine rank_key
        stories = self.story_repo.get_by_project(project_id)
        
        if not stories:
            # First story in project
            rank_key = generate_rank_key()
        elif after_story_id is None:
            # Append to end
            last_rank = stories[-1].rank_key
            rank_key = generate_rank_key(before=last_rank)
        else:
            # Insert after specific story
            after_idx = next((i for i, s in enumerate(stories) if s.id == after_story_id), None)
            if after_idx is None:
                raise ValueError(f"Story {after_story_id} not found in project")
            
            before_rank = stories[after_idx].rank_key
            after_rank = stories[after_idx + 1].rank_key if after_idx + 1 < len(stories) else None
            rank_key = generate_rank_key(before=before_rank, after=after_rank)

        story = Story(
            project_id=project_id,
            title=title,
            rank_key=rank_key,
            synopsis=synopsis,
            status=status,
        )

        return self.story_repo.create(story)


class ListStoriesUseCase:
    """List all stories in a project."""

    def __init__(self, story_repo: IStoryRepository):
        self.story_repo = story_repo

    def execute(self, project_id: UUID) -> List[Story]:
        """
        List all stories in a project, ordered by rank_key.
        
        Args:
            project_id: Project ID
            
        Returns:
            List of Story entities
        """
        return self.story_repo.get_by_project(project_id)


class UpdateStoryUseCase:
    """Update story metadata."""

    def __init__(self, story_repo: IStoryRepository):
        self.story_repo = story_repo

    def execute(
        self,
        story_id: UUID,
        title: Optional[str] = None,
        synopsis: Optional[str] = None,
        status: Optional[str] = None,
        exclude_from_ai: Optional[bool] = None,
    ) -> Story:
        """
        Update story metadata.
        
        Args:
            story_id: Story ID
            title: New title (optional)
            synopsis: New synopsis (optional)
            status: New status (optional)
            exclude_from_ai: New AI exclusion flag (optional)
            
        Returns:
            Updated Story entity
        """
        story = self.story_repo.get_by_id(story_id)
        if not story:
            raise ValueError(f"Story {story_id} not found")

        if title is not None:
            story.title = title
        if synopsis is not None:
            story.synopsis = synopsis
        if status is not None:
            story.status = status
        if exclude_from_ai is not None:
            story.exclude_from_ai = exclude_from_ai

        return self.story_repo.update(story)


class ReorderStoryUseCase:
    """Reorder a story within its project."""

    def __init__(self, story_repo: IStoryRepository):
        self.story_repo = story_repo

    def execute(self, story_id: UUID, after_story_id: Optional[UUID]) -> Story:
        """
        Move a story to a new position.
        
        Args:
            story_id: Story to move
            after_story_id: Story to insert after (None = move to beginning)
            
        Returns:
            Updated Story entity with new rank_key
        """
        story = self.story_repo.get_by_id(story_id)
        if not story:
            raise ValueError(f"Story {story_id} not found")

        # Get all stories in the project
        stories = self.story_repo.get_by_project(story.project_id)
        
        # Remove current story from the list to find neighbors
        other_stories = [s for s in stories if s.id != story_id]

        if not other_stories:
            # Only one story, no need to reorder
            return story

        if after_story_id is None:
            # Move to beginning
            first_rank = other_stories[0].rank_key
            story.rank_key = generate_rank_key(after=first_rank)
        else:
            # Find the target position
            after_idx = next((i for i, s in enumerate(other_stories) if s.id == after_story_id), None)
            if after_idx is None:
                raise ValueError(f"Story {after_story_id} not found")
            
            before_rank = other_stories[after_idx].rank_key
            after_rank = other_stories[after_idx + 1].rank_key if after_idx + 1 < len(other_stories) else None
            story.rank_key = generate_rank_key(before=before_rank, after=after_rank)

        return self.story_repo.update(story)


class DeleteStoryUseCase:
    """Delete a story and all its contents."""

    def __init__(self, story_repo: IStoryRepository):
        self.story_repo = story_repo

    def execute(self, story_id: UUID) -> None:
        """
        Delete a story.
        
        Args:
            story_id: Story ID
        """
        story = self.story_repo.get_by_id(story_id)
        if not story:
            raise ValueError(f"Story {story_id} not found")

        self.story_repo.delete(story_id)
