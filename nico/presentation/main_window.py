"""Main window for Nico application."""
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QLabel,
    QStatusBar,
    QMenuBar,
    QMessageBox,
)

from nico.presentation.widgets.binder import BinderWidget
from nico.presentation.widgets.editor import EditorWidget
from nico.presentation.widgets.right_panel import RightPanelWidget
from nico.presentation.widgets.empty_state import EmptyStateWidget
from nico.presentation.widgets.preferences_dialog import PreferencesDialog
from nico.presentation.widgets.template_dialog import TemplateSelectionDialog
from nico.presentation.widgets.llm_team_dialog import LLMTeamDialog
from nico.presentation.widgets.character_dialog import CharacterDialog
from nico.presentation.widgets.location_dialog import LocationDialog
from nico.presentation.widgets.event_dialog import EventDialog
from nico.application.context import get_app_context
from nico.preferences import get_preferences
from nico.theme import Theme


class MainWindow(QMainWindow):
    """Main application window with Scrivener-like layout."""
    
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Nico - Narrative Insight Composition Output")
        self.setGeometry(100, 100, 1400, 900)
        
        # Get application context and preferences
        self.app_context = get_app_context()
        self.prefs = get_preferences()
        
        # Apply theme
        self._apply_theme()
        
        # Create UI components
        self._setup_menubar()
        self._setup_central_widget()
        self._setup_statusbar()
        
        # Load the first project if available
        self._load_initial_project()
        
    def _setup_menubar(self) -> None:
        """Create the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        file_menu.addAction("&New Project...", self._on_new_project)
        file_menu.addAction("&Open Project...", self._on_open_project)
        file_menu.addSeparator()
        file_menu.addAction("&Save", self._on_save)
        file_menu.addAction("Save &As...", self._on_save_as)
        file_menu.addSeparator()
        file_menu.addAction("E&xit", self.close)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        edit_menu.addAction("&Undo")
        edit_menu.addAction("&Redo")
        edit_menu.addSeparator()
        edit_menu.addAction("Cu&t")
        edit_menu.addAction("&Copy")
        edit_menu.addAction("&Paste")
        edit_menu.addSeparator()
        edit_menu.addAction("Prefere&nces...", self._on_preferences)
        
        # Project menu
        project_menu = menubar.addMenu("&Project")
        project_menu.addAction("New &Story...")
        project_menu.addAction("New &Character...", self._on_manage_characters)
        project_menu.addAction("New &Event...", self._on_manage_events)
        project_menu.addAction("New &Location...", self._on_manage_locations)
        project_menu.addSeparator()
        project_menu.addAction("Generate Story from &Template...", self._on_generate_from_template)
        project_menu.addSeparator()
        project_menu.addAction("Project &Settings...")
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        tools_menu.addAction("&Characters...", self._on_manage_characters)
        tools_menu.addAction("&Locations...", self._on_manage_locations)
        tools_menu.addAction("&Events/Timeline...", self._on_manage_events)
        tools_menu.addSeparator()
        tools_menu.addAction("🤖 Configure AI &Team...", self._on_configure_llm_team)
        tools_menu.addSeparator()
        tools_menu.addAction("&Word Count Statistics...")
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        # AI Modules submenu
        ai_modules_menu = view_menu.addMenu("🤖 AI &Modules")
        
        self.module_quick_actions = ai_modules_menu.addAction("⚡ Quick Actions")
        self.module_quick_actions.setCheckable(True)
        self.module_quick_actions.setChecked(self.prefs.ai_modules.get("quick_actions", True))
        self.module_quick_actions.triggered.connect(lambda: self._toggle_ai_module("quick_actions"))
        
        self.module_chat = ai_modules_menu.addAction("💬 Chat")
        self.module_chat.setCheckable(True)
        self.module_chat.setChecked(self.prefs.ai_modules.get("chat", True))
        self.module_chat.triggered.connect(lambda: self._toggle_ai_module("chat"))
        
        self.module_context = ai_modules_menu.addAction("📍 Context Info")
        self.module_context.setCheckable(True)
        self.module_context.setChecked(self.prefs.ai_modules.get("context_info", True))
        self.module_context.triggered.connect(lambda: self._toggle_ai_module("context_info"))
        
        self.module_model_selector = ai_modules_menu.addAction("🤖 Model Selector")
        self.module_model_selector.setCheckable(True)
        self.module_model_selector.setChecked(self.prefs.ai_modules.get("model_selector", True))
        self.module_model_selector.triggered.connect(lambda: self._toggle_ai_module("model_selector"))
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        help_menu.addAction("&About Nico", self._on_about)
        help_menu.addAction("&Documentation")
        
    def _setup_central_widget(self) -> None:
        """Create the central widget with three-panel layout."""
        # Main horizontal splitter
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Empty state widget (shown when no projects exist)
        self.empty_state = EmptyStateWidget()
        self.empty_state.create_project_requested.connect(self._on_new_project)
        
        # Left panel: Binder (project tree)
        self.binder = BinderWidget()
        self.binder.project_selected.connect(self._on_project_selected)
        self.binder.story_selected.connect(self._on_story_selected)
        self.binder.chapter_selected.connect(self._on_chapter_selected)
        self.binder.scene_selected.connect(self._on_scene_selected)
        self.binder.character_selected.connect(self._on_character_selected)
        self.binder.location_selected.connect(self._on_location_selected)
        self.binder.event_selected.connect(self._on_event_selected)
        
        # Connect collection selections
        self.binder.stories_collection_selected.connect(self._on_stories_collection_selected)
        self.binder.characters_collection_selected.connect(self._on_characters_collection_selected)
        
        # Connect item deletion to show appropriate overview
        self.binder.item_deleted.connect(self._on_item_deleted)
        
        self.main_splitter.addWidget(self.binder)
        
        # Center panel: Editor
        self.editor = EditorWidget()
        # Connect editor's navigation signals (from double-clicks in overviews)
        self.editor.story_selected.connect(self._on_story_selected)
        self.editor.chapter_selected.connect(self._on_chapter_selected)
        self.editor.scene_selected.connect(self._on_scene_selected)
        self.editor.character_selected.connect(self._on_character_selected)
        
        # Connect character profile and overview updates to refresh binder
        self.editor.character_profile.character_updated.connect(self._on_character_updated)
        self.editor.characters_overview.character_updated.connect(self._on_character_updated)
        
        # Connect stories overview updates to refresh binder
        self.editor.stories_overview.story_updated.connect(self._on_story_updated)
        
        self.main_splitter.addWidget(self.editor)
        
        # Right panel: Tabbed Inspector and AI
        self.right_panel = RightPanelWidget()
        self.main_splitter.addWidget(self.right_panel)
        
        # Set initial sizes (20%, 50%, 30%)
        self.main_splitter.setSizes([280, 700, 420])
        
        self.setCentralWidget(self.main_splitter)
        
    def _setup_statusbar(self) -> None:
        """Create the status bar."""
        status_bar = QStatusBar()
        status_bar.showMessage("Ready")
        self.setStatusBar(status_bar)
    
    def _load_initial_project(self) -> None:
        """Load the first available project and auto-select it."""
        try:
            projects = self.app_context.project_service.list_projects()
            if projects:
                # TODO: Load last-used project from settings/preferences
                # For now, load the first project
                project = self.app_context.project_service.get_project(projects[0].id)
                if project:
                    # Load project into binder
                    self.binder.load_project(project)
                    
                    # Auto-select the project in the binder to populate the UI
                    # Find and select the project item in the tree
                    tree = self.binder.tree
                    if tree.topLevelItemCount() > 0:
                        project_item = tree.topLevelItem(0)
                        tree.setCurrentItem(project_item)
                        # Trigger the selection signal
                        self._on_project_selected(project.id)
                    
                    self.statusBar().showMessage(f"Loaded project: {project.title}")
                else:
                    self.statusBar().showMessage("No project data available")
                    self._show_empty_state()
            else:
                # No projects exist - show empty state
                self._show_empty_state()
                self.statusBar().showMessage("No projects found. Create a new project to get started.")
        except Exception as e:
            self.statusBar().showMessage(f"Error loading project: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to load project: {str(e)}")
            self._show_empty_state()
    
    def _show_empty_state(self) -> None:
        """Show the empty state widget when no projects exist."""
        self.setCentralWidget(self.empty_state)
    
    def _show_normal_layout(self) -> None:
        """Show the normal three-panel layout."""
        self.setCentralWidget(self.main_splitter)
    
    def _on_project_selected(self, project_id: int) -> None:
        """Handle project selection from binder."""
        try:
            project = self.app_context.project_service.get_project(project_id)
            if project:
                self.editor.show_project(project)
                self.right_panel.set_project_context(project)
                self.binder.select_project(project_id)
                self.statusBar().showMessage(f"Viewing project: {project.title}")
        except Exception as e:
            self.statusBar().showMessage(f"Error loading project: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to load project: {str(e)}")
    
    def _on_story_selected(self, story_id: int) -> None:
        """Handle story selection from binder."""
        try:
            # Get story through project hierarchy
            if self.binder.current_project:
                story = next(
                    (s for s in self.binder.current_project.stories if s.id == story_id),
                    None
                )
                if story:
                    self.editor.show_story(story)
                    self.right_panel.set_story_context(story)
                    self.binder.select_story(story_id)
                    self.statusBar().showMessage(f"Viewing story: {story.title}")
                else:
                    raise ValueError(f"Story {story_id} not found in project")
            else:
                raise ValueError("No project loaded")
        except Exception as e:
            self.statusBar().showMessage(f"Error loading story: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to load story: {str(e)}")
    
    def _on_chapter_selected(self, chapter_id: int) -> None:
        """Handle chapter selection from binder."""
        try:
            # Get chapter through project hierarchy
            if self.binder.current_project:
                chapter = None
                for story in self.binder.current_project.stories:
                    chapter = next(
                        (c for c in story.chapters if c.id == chapter_id),
                        None
                    )
                    if chapter:
                        break
                
                if chapter:
                    self.editor.show_chapter(chapter)
                    self.right_panel.set_chapter_context(chapter)
                    self.binder.select_chapter(chapter_id)
                    self.statusBar().showMessage(f"Viewing chapter: {chapter.title}")
                else:
                    raise ValueError(f"Chapter {chapter_id} not found in project")
            else:
                raise ValueError("No project loaded")
        except Exception as e:
            self.statusBar().showMessage(f"Error loading chapter: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to load chapter: {str(e)}")
    
    def _on_scene_selected(self, scene_id: int) -> None:
        """Handle scene selection from binder."""
        try:
            scene = self.app_context.scene_service.get_scene(scene_id)
            if scene:
                self.editor.show_scene(scene)
                self.right_panel.set_scene_context(scene)
                self.binder.select_scene(scene_id)
                self.statusBar().showMessage(f"Loaded scene: {scene.title}")
        except Exception as e:
            self.statusBar().showMessage(f"Error loading scene: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to load scene: {str(e)}")
        
    # Menu action handlers (placeholders)
    def _on_new_project(self) -> None:
        """Handle New Project action."""
        self.statusBar().showMessage("New Project (not implemented)")
        
    def _on_open_project(self) -> None:
        """Handle Open Project action."""
        self.statusBar().showMessage("Open Project (not implemented)")
        
    def _on_save(self) -> None:
        """Handle Save action."""
        self.statusBar().showMessage("Save (not implemented)")
        
    def _on_save_as(self) -> None:
        """Handle Save As action."""
        self.statusBar().showMessage("Save As (not implemented)")
    
    def _on_preferences(self) -> None:
        """Show preferences dialog."""
        dialog = PreferencesDialog(self)
        dialog.preferences_changed.connect(self._on_preferences_changed)
        dialog.exec()
    
    def _on_configure_llm_team(self) -> None:
        """Show LLM team configuration dialog."""
        dialog = LLMTeamDialog(self)
        dialog.team_updated.connect(self._on_llm_team_updated)
        dialog.exec()
    
    def _on_llm_team_updated(self) -> None:
        """Handle LLM team configuration changes."""
        # Notify AI panel to refresh
        if hasattr(self, 'right_panel') and hasattr(self.right_panel, 'ai_panel'):
            self.right_panel.ai_panel.refresh_from_team_update()
    
    def _on_generate_from_template(self) -> None:
        """Show template selection dialog and generate story."""
        if not self.binder.current_project:
            QMessageBox.warning(
                self,
                "No Project",
                "Please select a project before generating a story from template."
            )
            return
        
        dialog = TemplateSelectionDialog(self)
        dialog.template_accepted.connect(self._generate_story_from_template)
        dialog.exec()
    
    def _generate_story_from_template(self, template, customization: dict) -> None:
        """Generate story from selected template."""
        try:
            # Extract story title if provided
            story_title = customization.pop("story_title", None)
            
            # Generate the story
            self.statusBar().showMessage("Generating story structure...")
            
            story = self.app_context.story_generator.generate_from_template(
                project=self.binder.current_project,
                template=template,
                story_title=story_title,
                customization=customization
            )
            
            # Refresh the binder to show new story
            self.binder.load_project(self.binder.current_project)
            
            # Select the new story
            self._on_story_selected(story.id)
            
            QMessageBox.information(
                self,
                "Story Generated",
                f"Successfully generated story: {story.title}\n\n"
                f"Created {len(story.chapters)} chapters with scenes.\n"
                f"You can now fill in the content for each scene."
            )
            
            self.statusBar().showMessage(f"Generated story: {story.title}")
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Generation Error",
                f"Failed to generate story: {str(e)}"
            )
            self.statusBar().showMessage(f"Error: {str(e)}")
    
    def _toggle_ai_module(self, module_name: str) -> None:
        """Toggle visibility of an AI module."""
        is_visible = self.prefs.ai_modules.get(module_name, True)
        new_state = not is_visible
        
        # Update the AI panel
        self.right_panel.ai_panel.set_module_visible(module_name, new_state)
        
        # Update menu checkboxes
        if module_name == "quick_actions":
            self.module_quick_actions.setChecked(new_state)
        elif module_name == "chat":
            self.module_chat.setChecked(new_state)
        elif module_name == "context_info":
            self.module_context.setChecked(new_state)
        elif module_name == "model_selector":
            self.module_model_selector.setChecked(new_state)
    
    def _on_preferences_changed(self) -> None:
        """Handle preferences changes."""
        self._apply_theme()
        self.statusBar().showMessage("Preferences saved. Some changes may require restart.")
    
    def _apply_theme(self) -> None:
        """Apply the current theme."""
        if self.prefs.theme == "dark":
            self.setStyleSheet(Theme.get_dark_theme())
        else:
            self.setStyleSheet(Theme.get_light_theme())
        
        # Apply font scaling (would affect all fonts in the app)
        # This could be enhanced to use QApplication.setFont() with scaled size
    
    def _on_about(self) -> None:
        """Show About dialog."""
        QMessageBox.about(
            self,
            "About Nico",
            "<h2>Nico</h2>"
            "<p>Narrative Insight Composition Output</p>"
            "<p>Version 0.1.0</p>"
            "<p>A privacy-first writing application for narrative creators.</p>"
        )
    
    def closeEvent(self, event) -> None:
        """Handle window close event."""
        # Clean up database connection
        self.app_context.close()
        event.accept()
    
    def _on_manage_characters(self) -> None:
        """Open character management dialog."""
        # Get current project
        # For now, we'll get the first project - in real usage, this should be the active project
        projects = self.app_context.project_service.list_projects()
        if not projects:
            QMessageBox.warning(
                self,
                "No Project",
                "Please create or open a project first."
            )
            return
        
        project = projects[0]  # Use first project for now
        
        # Show character creation dialog
        dialog = CharacterDialog(project.id, parent=self)
        if dialog.exec():
            # Character was created/updated, refresh the binder if needed
            self.statusBar().showMessage("Character saved", 3000)
    
    def _on_manage_locations(self) -> None:
        """Open location management dialog."""
        # Get current project
        projects = self.app_context.project_service.list_projects()
        if not projects:
            QMessageBox.warning(
                self,
                "No Project",
                "Please create or open a project first."
            )
            return
        
        project = projects[0]  # Use first project for now
        
        # Show location creation dialog
        dialog = LocationDialog(project.id, parent=self)
        if dialog.exec():
            # Location was created/updated, refresh the binder if needed
            self.statusBar().showMessage("Location saved", 3000)
    
    def _on_manage_events(self) -> None:
        """Open event/timeline management dialog."""
        # Get current project
        projects = self.app_context.project_service.list_projects()
        if not projects:
            QMessageBox.warning(
                self,
                "No Project",
                "Please create or open a project first."
            )
            return
        
        project = projects[0]  # Use first project for now
        
        # Show event creation dialog
        dialog = EventDialog(project.id, parent=self)
        if dialog.exec():
            # Event was created/updated, refresh the binder if needed
            self.statusBar().showMessage("Event saved", 3000)
    
    def _on_character_selected(self, character_id: int) -> None:
        """Handle character selection from binder."""
        try:
            self.editor.show_character(character_id)
            # TODO: Set character context in right panel when implemented
            self.statusBar().showMessage("Viewing character profile")
        except Exception as e:
            self.statusBar().showMessage(f"Error loading character: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to load character: {str(e)}")
    
    def _on_location_selected(self, location_id: int) -> None:
        """Handle location selection from binder."""
        try:
            self.editor.show_location(location_id)
            # TODO: Set location context in right panel when implemented
            self.statusBar().showMessage("Viewing location")
        except Exception as e:
            self.statusBar().showMessage(f"Error loading location: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to load location: {str(e)}")
    
    def _on_event_selected(self, event_id: int) -> None:
        """Handle event selection from binder."""
        try:
            self.editor.show_event(event_id)
            # TODO: Set event context in right panel when implemented
            self.statusBar().showMessage("Viewing event")
        except Exception as e:
            self.statusBar().showMessage(f"Error loading event: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to load event: {str(e)}")
    
    def _on_stories_collection_selected(self) -> None:
        """Handle Stories collection selection from binder."""
        if self.binder.current_project:
            self.editor.show_stories_overview(self.binder.current_project)
            self.statusBar().showMessage("Viewing stories overview")
    
    def _on_characters_collection_selected(self) -> None:
        """Handle Characters collection selection from binder."""
        if self.binder.current_project:
            self.editor.show_characters_overview(self.binder.current_project)
            self.statusBar().showMessage("Viewing characters overview")
    
    def _on_character_updated(self) -> None:
        """Handle character updates (create/edit/delete) - refresh binder and show overview."""
        if self.binder.current_project:
            # Reload project to refresh binder
            refreshed_project = self.app_context.project_service.get_project(self.binder.current_project.id)
            if refreshed_project:
                self.binder.load_project(refreshed_project)
                # Show characters overview after deletion/update
                self.editor.show_characters_overview(refreshed_project)
                self.statusBar().showMessage("Characters updated")
    
    def _on_story_updated(self) -> None:
        """Handle story updates (create/edit/delete) - refresh binder and show overview."""
        if self.binder.current_project:
            # Reload project to refresh binder
            refreshed_project = self.app_context.project_service.get_project(self.binder.current_project.id)
            if refreshed_project:
                self.binder.load_project(refreshed_project)
                # Show stories overview after deletion/update
                self.editor.show_stories_overview(refreshed_project)
                self.statusBar().showMessage("Stories updated")
    
    def _on_item_deleted(self, item_type: str) -> None:
        """Handle item deletion from binder - show appropriate overview."""
        if not self.binder.current_project:
            return
        
        # Show appropriate overview based on what was deleted
        if item_type in ("story", "chapter", "scene"):
            self.editor.show_stories_overview(self.binder.current_project)
        elif item_type == "character":
            self.editor.show_characters_overview(self.binder.current_project)
        # For locations and events, we could add overviews later
