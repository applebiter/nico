"""AI panel widget - context-aware AI tools with modular sections."""
from typing import Optional, Literal, Dict

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QLineEdit,
    QPushButton,
    QLabel,
    QComboBox,
    QGroupBox,
    QScrollArea,
    QCheckBox,
)

from nico.domain.models import Project, Story, Chapter, Scene
from nico.preferences import get_preferences
from nico.application.ai_service import get_ai_service

ContextType = Literal["project", "story", "chapter", "scene"]


class AIPanelWidget(QWidget):
    """AI tools panel that adapts based on context level with modular sections."""
    
    modules_changed = Signal()  # Emitted when module visibility changes
    
    def __init__(self) -> None:
        super().__init__()
        self.context_type: Optional[ContextType] = None
        self.current_entity = None
        self.prefs = get_preferences()
        self.ai_service = get_ai_service()
        
        # Module widgets
        self.module_widgets: Dict[str, QWidget] = {}
        
        # Connect AI service signals
        self.ai_service.response_ready.connect(self._on_ai_response)
        self.ai_service.error.connect(self._on_ai_error)
        self.ai_service.generating.connect(self._on_generating_changed)
        
        self._setup_ui()
        self._apply_module_visibility()
        self._refresh_model_selector()
        
    def _setup_ui(self) -> None:
        """Set up the widget layout with modular sections."""
        # Main scroll area to contain all modules
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        container = QWidget()
        self.main_layout = QVBoxLayout(container)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(10)
        
        # Module: Header with model selector
        self._create_model_selector_module()
        
        # Module: Context info
        self._create_context_module()
        
        # Module: Quick actions
        self._create_quick_actions_module()
        
        # Module: Chat interface
        self._create_chat_module()
        
        # Add stretch at the end
        self.main_layout.addStretch()
        
        scroll.setWidget(container)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)
        self.setLayout(layout)
    
    def _create_model_selector_module(self) -> None:
        """Create the model selector module."""
        module = QGroupBox("🤖 AI Model")
        layout = QHBoxLayout()
        
        self.model_selector = QComboBox()
        self.model_selector.setToolTip("Select AI model")
        layout.addWidget(QLabel("Model:"))
        layout.addWidget(self.model_selector)
        
        refresh_btn = QPushButton("🔄")
        refresh_btn.setToolTip("Refresh available models")
        refresh_btn.setMaximumWidth(30)
        refresh_btn.clicked.connect(self._refresh_model_selector)
        layout.addWidget(refresh_btn)
        
        module.setLayout(layout)
        self.module_widgets["model_selector"] = module
        self.main_layout.addWidget(module)
    
    def _refresh_model_selector(self) -> None:
        """Refresh the model selector with available LLMs."""
        self.model_selector.clear()
        
        try:
            llms = self.ai_service.list_available_llms()
        except Exception as e:
            print(f"Error loading LLMs: {e}")
            llms = []
        
        if not llms:
            self.model_selector.addItem("⚠️ No AI configured (Tools → Configure AI Team)", None)
            self.model_selector.setEnabled(False)
            return
        
        self.model_selector.setEnabled(True)
        
        # Add primary first
        primary = self.ai_service.get_primary_llm()
        if primary:
            icon = "⭐" if primary.enabled else "💤"
            self.model_selector.addItem(
                f"{icon} {primary.name} (Primary)", 
                primary.id
            )
        
        # Add other members
        for llm in llms:
            if primary and llm.id == primary.id:
                continue  # Already added as primary
            
            icon = "✓" if llm.enabled else "💤"
            self.model_selector.addItem(f"{icon} {llm.name}", llm.id)
    
    def _create_context_module(self) -> None:
        """Create the context info module."""
        module = QGroupBox("📍 Current Context")
        layout = QVBoxLayout()
        
        self.context_label = QLabel("No context loaded")
        self.context_label.setWordWrap(True)
        self.context_label.setStyleSheet("font-size: 12px;")
        layout.addWidget(self.context_label)
        
        module.setLayout(layout)
        self.module_widgets["context_info"] = module
        self.main_layout.addWidget(module)
    
    def _create_quick_actions_module(self) -> None:
        """Create the quick actions module."""
        self.actions_group = QGroupBox("⚡ Quick Actions")
        self.actions_layout = QVBoxLayout()
        self.actions_group.setLayout(self.actions_layout)
        
        self.module_widgets["quick_actions"] = self.actions_group
        self.main_layout.addWidget(self.actions_group)
        
        # Initialize with project context
        self._update_actions_for_context("project")
    
    def _create_chat_module(self) -> None:
        """Create the chat interface module."""
        module = QGroupBox("💬 Chat")
        layout = QVBoxLayout()
        
        # Chat history
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setPlaceholderText("AI conversation will appear here...")
        self.chat_history.setMaximumHeight(200)
        layout.addWidget(self.chat_history)
        
        # Input area
        input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Ask the AI assistant...")
        self.chat_input.returnPressed.connect(self._send_message)
        input_layout.addWidget(self.chat_input)
        
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self._send_message)
        input_layout.addWidget(self.send_btn)
        
        layout.addLayout(input_layout)
        
        module.setLayout(layout)
        self.module_widgets["chat"] = module
        self.main_layout.addWidget(module)
    
    def set_module_visible(self, module_name: str, visible: bool) -> None:
        """Show or hide a specific module."""
        if module_name in self.module_widgets:
            self.module_widgets[module_name].setVisible(visible)
            # Update preferences
            self.prefs.ai_modules[module_name] = visible
            self.prefs.save()
            self.modules_changed.emit()
    
    def _apply_module_visibility(self) -> None:
        """Apply module visibility from preferences."""
        for module_name, widget in self.module_widgets.items():
            visible = self.prefs.ai_modules.get(module_name, True)
            widget.setVisible(visible)
        
    def set_project_context(self, project: Project) -> None:
        """Set context to project level."""
        self.context_type = "project"
        self.current_entity = project
        self.context_label.setText(f"📚 Project: {project.title}")
        self._update_actions_for_context("project")
        
    def set_story_context(self, story: Story) -> None:
        """Set context to story level."""
        self.context_type = "story"
        self.current_entity = story
        self.context_label.setText(f"📖 Story: {story.title}")
        self._update_actions_for_context("story")
        
    def set_chapter_context(self, chapter: Chapter) -> None:
        """Set context to chapter level."""
        self.context_type = "chapter"
        self.current_entity = chapter
        self.context_label.setText(f"📑 Chapter {chapter.number}: {chapter.title}")
        self._update_actions_for_context("chapter")
        
    def set_scene_context(self, scene: Scene) -> None:
        """Set context to scene level."""
        self.context_type = "scene"
        self.current_entity = scene
        self.context_label.setText(f"✍️ Scene: {scene.title}")
        self._update_actions_for_context("scene")
        
    def _update_actions_for_context(self, context: ContextType) -> None:
        """Update quick actions based on context level."""
        # Clear existing actions
        while self.actions_layout.count():
            item = self.actions_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add context-specific actions
        if context == "project":
            self._add_action_button("💡 Analyze Universe", "Review world consistency and character arcs")
            self._add_action_button("🎭 Character Analysis", "Deep dive into character relationships")
            self._add_action_button("🗺️ World Building", "Explore locations and events")
            self._add_action_button("📊 Project Summary", "Generate overview and statistics")
            
        elif context == "story":
            self._add_action_button("📝 Plot Analysis", "Analyze story structure and pacing")
            self._add_action_button("🎯 Beat Sheet", "Review/generate story beats")
            self._add_action_button("🔍 Continuity Check", "Check for plot holes and inconsistencies")
            self._add_action_button("✨ Generate Outline", "Create or refine chapter outline")
            
        elif context == "chapter":
            self._add_action_button("🎬 Scene Breakdown", "Analyze scene structure")
            self._add_action_button("💬 Dialogue Review", "Evaluate dialogue quality")
            self._add_action_button("🔄 Suggest Reorder", "Recommend scene sequence")
            self._add_action_button("📄 Chapter Summary", "Generate chapter synopsis")
            
        elif context == "scene":
            self._add_action_button("✍️ Improve Writing", "Suggest edits and enhancements")
            self._add_action_button("🎭 Character Voice", "Check character consistency")
            self._add_action_button("🎨 Show Don't Tell", "Identify areas to strengthen")
            self._add_action_button("➕ Continue Writing", "Generate next paragraph")
            self._add_action_button("🔄 Rewrite", "Rephrase with different tone")
        
        self.actions_layout.addStretch()
        
    def _add_action_button(self, text: str, tooltip: str) -> None:
        """Add an action button to the layout."""
        btn = QPushButton(text)
        btn.setToolTip(tooltip)
        btn.clicked.connect(lambda: self._execute_action(text))
        self.actions_layout.addWidget(btn)
        
    def _execute_action(self, action: str) -> None:
        """Execute a quick action."""
        self.chat_history.append(f"<b>🎬 Action:</b> {action}")
        
        # Build prompt based on action and context
        prompt = self._build_action_prompt(action)
        
        # Get selected LLM
        llm_id = self.model_selector.currentData()
        
        # Generate response
        self.ai_service.generate(prompt, llm_id)
    
    def _build_action_prompt(self, action: str) -> str:
        """Build a prompt for the given action and current context."""
        context_info = ""
        if self.current_entity:
            if hasattr(self.current_entity, 'title'):
                context_info = f"Title: {self.current_entity.title}\n"
            if hasattr(self.current_entity, 'synopsis'):
                context_info += f"Synopsis: {self.current_entity.synopsis}\n"
            if hasattr(self.current_entity, 'body'):
                context_info += f"Content: {self.current_entity.body[:500]}...\n"
        
        prompt = f"""Action: {action}
Context Type: {self.context_type}
{context_info}
Please provide a helpful response for this action."""
        
        return prompt
        
    def _send_message(self) -> None:
        """Send a chat message."""
        message = self.chat_input.text().strip()
        if not message:
            return
        
        self.chat_history.append(f"<b>👤 You:</b> {message}")
        self.chat_input.clear()
        
        # Add context to the message
        if self.current_entity:
            context_note = f"\n<i>Context: {self.context_type}</i>"
            message = message + context_note
        
        # Get selected LLM
        llm_id = self.model_selector.currentData()
        
        # Generate response
        self.ai_service.generate(message, llm_id)
    
    def _on_ai_response(self, response: str, llm_id: str) -> None:
        """Handle AI response."""
        # Find LLM name
        llm_name = llm_id
        for i in range(self.model_selector.count()):
            if self.model_selector.itemData(i) == llm_id:
                llm_name = self.model_selector.itemText(i)
                break
        
        self.chat_history.append(f"<b>🤖 {llm_name}:</b> {response}")
        self.chat_history.append("<hr>")
        
        # Scroll to bottom
        scrollbar = self.chat_history.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def _on_ai_error(self, error_msg: str) -> None:
        """Handle AI error."""
        self.chat_history.append(f"<b>❌ Error:</b> <span style='color: red;'>{error_msg}</span>")
        self.chat_history.append("<hr>")
    
    def _on_generating_changed(self, is_generating: bool) -> None:
        """Handle generating state change."""
        self.send_btn.setEnabled(not is_generating)
        self.chat_input.setEnabled(not is_generating)
        
        if is_generating:
            self.send_btn.setText("...")
            self.chat_history.append("<i>⏳ Generating...</i>")
        else:
            self.send_btn.setText("Send")
    
    def refresh_from_team_update(self) -> None:
        """Refresh panel after team configuration changes."""
        self._refresh_model_selector()
