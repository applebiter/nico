"""Application use cases."""

from .chapter import (
    CreateChapterUseCase,
    DeleteChapterUseCase,
    ListChaptersUseCase,
    ReorderChapterUseCase,
    UpdateChapterUseCase,
)
from .project import (
    CreateProjectUseCase,
    GetProjectUseCase,
    OpenProjectUseCase,
    UpdateProjectUseCase,
)
from .scene import (
    CreateSceneUseCase,
    DeleteSceneUseCase,
    GetSceneDocumentUseCase,
    GetSceneRevisionsUseCase,
    ListScenesUseCase,
    ReorderSceneUseCase,
    UpdateSceneDocumentUseCase,
    UpdateSceneUseCase,
)
from .story import (
    CreateStoryUseCase,
    DeleteStoryUseCase,
    ListStoriesUseCase,
    ReorderStoryUseCase,
    UpdateStoryUseCase,
)

__all__ = [
    # Project use cases
    "CreateProjectUseCase",
    "OpenProjectUseCase",
    "UpdateProjectUseCase",
    "GetProjectUseCase",
    # Story use cases
    "CreateStoryUseCase",
    "ListStoriesUseCase",
    "UpdateStoryUseCase",
    "ReorderStoryUseCase",
    "DeleteStoryUseCase",
    # Chapter use cases
    "CreateChapterUseCase",
    "ListChaptersUseCase",
    "UpdateChapterUseCase",
    "ReorderChapterUseCase",
    "DeleteChapterUseCase",
    # Scene use cases
    "CreateSceneUseCase",
    "ListScenesUseCase",
    "UpdateSceneUseCase",
    "UpdateSceneDocumentUseCase",
    "GetSceneDocumentUseCase",
    "GetSceneRevisionsUseCase",
    "ReorderSceneUseCase",
    "DeleteSceneUseCase",
]
