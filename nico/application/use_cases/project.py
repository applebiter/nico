"""Use cases for Project operations."""

from pathlib import Path
from typing import Optional
from uuid import UUID

from nico.domain.models import Project
from nico.domain.repositories import IProjectRepository
from nico.infrastructure.persistence import Database


class CreateProjectUseCase:
    """Create a new project in a folder."""

    def __init__(self, project_repo: IProjectRepository, database: Database):
        self.project_repo = project_repo
        self.database = database

    def execute(
        self,
        name: str,
        path: Path,
        description: Optional[str] = None,
        author: Optional[str] = None,
        local_only_ai: bool = True,
    ) -> Project:
        """
        Create a new project.
        
        Args:
            name: Project name
            path: Path to project folder
            description: Optional project description
            author: Optional author name
            local_only_ai: Whether to restrict AI to local-only (default True)
            
        Returns:
            Created Project entity
            
        Raises:
            ValueError: If project folder already exists or path already in use
        """
        # Ensure the path doesn't already have a project
        existing = self.project_repo.get_by_path(path)
        if existing:
            raise ValueError(f"Project already exists at {path}")

        # Create project folder structure
        path.mkdir(parents=True, exist_ok=True)
        (path / "media").mkdir(exist_ok=True)
        (path / "exports").mkdir(exist_ok=True)
        (path / "cache").mkdir(exist_ok=True)

        # Create project entity
        project = Project(
            name=name,
            path=path,
            description=description,
            author=author,
            local_only_ai=local_only_ai,
        )

        # Initialize database in project folder
        db_path = path / "project.sqlite3"
        if not db_path.exists():
            # Create tables
            self.database.create_tables()

        # Save project to database
        return self.project_repo.create(project)


class OpenProjectUseCase:
    """Open an existing project."""

    def __init__(self, project_repo: IProjectRepository):
        self.project_repo = project_repo

    def execute(self, path: Path) -> Project:
        """
        Open a project by its folder path.
        
        Args:
            path: Path to project folder
            
        Returns:
            Project entity
            
        Raises:
            ValueError: If no project exists at the path
        """
        # Verify project folder structure
        if not path.exists() or not path.is_dir():
            raise ValueError(f"Project folder not found: {path}")

        db_path = path / "project.sqlite3"
        if not db_path.exists():
            raise ValueError(f"Project database not found: {db_path}")

        # Load project from database
        project = self.project_repo.get_by_path(path)
        if not project:
            raise ValueError(f"No project found at {path}")

        return project


class UpdateProjectUseCase:
    """Update project metadata."""

    def __init__(self, project_repo: IProjectRepository):
        self.project_repo = project_repo

    def execute(
        self,
        project_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        author: Optional[str] = None,
        bibliography_style: Optional[str] = None,
        local_only_ai: Optional[bool] = None,
    ) -> Project:
        """
        Update project metadata.
        
        Args:
            project_id: Project ID
            name: New name (optional)
            description: New description (optional)
            author: New author (optional)
            bibliography_style: New citation style (optional)
            local_only_ai: New AI restriction setting (optional)
            
        Returns:
            Updated Project entity
            
        Raises:
            ValueError: If project not found
        """
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Update fields if provided
        if name is not None:
            project.name = name
        if description is not None:
            project.description = description
        if author is not None:
            project.author = author
        if bibliography_style is not None:
            project.bibliography_style = bibliography_style
        if local_only_ai is not None:
            project.local_only_ai = local_only_ai

        return self.project_repo.update(project)


class GetProjectUseCase:
    """Retrieve project information."""

    def __init__(self, project_repo: IProjectRepository):
        self.project_repo = project_repo

    def execute(self, project_id: UUID) -> Optional[Project]:
        """
        Get a project by ID.
        
        Args:
            project_id: Project ID
            
        Returns:
            Project entity or None if not found
        """
        return self.project_repo.get_by_id(project_id)
