"""LLM Team configuration wizard dialog."""
import asyncio
from typing import List, Dict, Any, Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QLineEdit,
    QSpinBox, QDoubleSpinBox, QCheckBox, QGroupBox, QTabWidget,
    QWidget, QProgressBar, QMessageBox, QHeaderView
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QColor

from nico.ai.providers import LLMConfig, ProviderType
from nico.ai.manager import get_llm_team
from nico.ai.discovery import discover_ollama_endpoints, check_local_ollama, get_local_subnet
from nico.preferences import get_preferences


class DiscoveryThread(QThread):
    """Thread for network discovery to avoid blocking UI."""
    
    progress = Signal(int, int)  # current, total
    finished = Signal(list)  # discovered endpoints
    
    def __init__(self, subnet: str):
        super().__init__()
        self.subnet = subnet
    
    def run(self):
        """Run discovery."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Check local first
            local = loop.run_until_complete(check_local_ollama())
            discovered = [local] if local else []
            
            # Then scan network
            network_results = loop.run_until_complete(
                discover_ollama_endpoints(self.subnet)
            )
            discovered.extend(network_results)
            
            self.finished.emit(discovered)
            
        except Exception as e:
            print(f"Discovery error: {e}")
            self.finished.emit([])


class LLMTeamDialog(QDialog):
    """Dialog for configuring the LLM team."""
    
    team_updated = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure AI Team")
        self.resize(900, 600)
        
        self.prefs = get_preferences()
        self.team = get_llm_team()
        self.discovered_endpoints: List[Dict[str, Any]] = []
        
        self._setup_ui()
        self._load_team()
    
    def _setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("<h2>🤖 AI Team Configuration</h2>")
        layout.addWidget(header)
        
        info = QLabel(
            "Build your team of AI assistants. Mix local Ollama models with cloud APIs. "
            "One AI is enough to get started, or assemble a whole team for different tasks."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #888; margin-bottom: 10px;")
        layout.addWidget(info)
        
        # Tabs for different sections
        tabs = QTabWidget()
        
        # Team members tab
        team_tab = QWidget()
        self._setup_team_tab(team_tab)
        tabs.addTab(team_tab, "Team Members")
        
        # Discovery tab
        discovery_tab = QWidget()
        self._setup_discovery_tab(discovery_tab)
        tabs.addTab(discovery_tab, "Discover Ollama")
        
        # Quick add tab
        quick_add_tab = QWidget()
        self._setup_quick_add_tab(quick_add_tab)
        tabs.addTab(quick_add_tab, "Add API Provider")
        
        layout.addWidget(tabs)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        test_btn = QPushButton("Test All")
        test_btn.clicked.connect(self._test_all)
        button_layout.addWidget(test_btn)
        
        warmup_btn = QPushButton("Warm Up All")
        warmup_btn.clicked.connect(self._warmup_all)
        button_layout.addWidget(warmup_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def _setup_team_tab(self, tab: QWidget):
        """Setup the team members tab."""
        layout = QVBoxLayout(tab)
        
        # Team table
        self.team_table = QTableWidget()
        self.team_table.setColumnCount(7)
        self.team_table.setHorizontalHeaderLabels([
            "Enabled", "Primary", "Name", "Provider", "Model", "Speed", "Actions"
        ])
        self.team_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.team_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addWidget(self.team_table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add Member")
        add_btn.clicked.connect(self._add_member_dialog)
        btn_layout.addWidget(add_btn)
        
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self._remove_selected)
        btn_layout.addWidget(remove_btn)
        
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
    
    def _setup_discovery_tab(self, tab: QWidget):
        """Setup the Ollama discovery tab."""
        layout = QVBoxLayout(tab)
        
        # Discovery controls
        controls = QGroupBox("Network Scanner")
        controls_layout = QVBoxLayout()
        
        subnet_layout = QHBoxLayout()
        subnet_layout.addWidget(QLabel("Subnet:"))
        self.subnet_input = QLineEdit(get_local_subnet())
        self.subnet_input.setPlaceholderText("192.168.1.0/24")
        subnet_layout.addWidget(self.subnet_input)
        
        discover_btn = QPushButton("Scan Network")
        discover_btn.clicked.connect(self._start_discovery)
        subnet_layout.addWidget(discover_btn)
        
        controls_layout.addLayout(subnet_layout)
        
        self.discovery_progress = QProgressBar()
        self.discovery_progress.setVisible(False)
        controls_layout.addWidget(self.discovery_progress)
        
        controls.setLayout(controls_layout)
        layout.addWidget(controls)
        
        # Discovered endpoints table
        self.discovered_table = QTableWidget()
        self.discovered_table.setColumnCount(4)
        self.discovered_table.setHorizontalHeaderLabels([
            "Hostname", "IP", "Models Available", "Actions"
        ])
        self.discovered_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(QLabel("<b>Discovered Endpoints:</b>"))
        layout.addWidget(self.discovered_table)
    
    def _setup_quick_add_tab(self, tab: QWidget):
        """Setup the quick add API provider tab."""
        layout = QVBoxLayout(tab)
        
        # OpenAI
        openai_group = QGroupBox("OpenAI")
        openai_layout = QVBoxLayout()
        
        openai_form = QHBoxLayout()
        openai_form.addWidget(QLabel("API Key:"))
        self.openai_key_input = QLineEdit()
        self.openai_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.openai_key_input.setPlaceholderText("sk-...")
        openai_form.addWidget(self.openai_key_input)
        
        openai_model = QComboBox()
        openai_model.addItems(["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"])
        openai_form.addWidget(openai_model)
        self.openai_model = openai_model
        
        add_openai_btn = QPushButton("Add to Team")
        add_openai_btn.clicked.connect(lambda: self._quick_add_api("openai"))
        openai_form.addWidget(add_openai_btn)
        
        openai_layout.addLayout(openai_form)
        openai_group.setLayout(openai_layout)
        layout.addWidget(openai_group)
        
        # Anthropic
        anthropic_group = QGroupBox("Anthropic Claude")
        anthropic_layout = QVBoxLayout()
        
        anthropic_form = QHBoxLayout()
        anthropic_form.addWidget(QLabel("API Key:"))
        self.anthropic_key_input = QLineEdit()
        self.anthropic_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.anthropic_key_input.setPlaceholderText("sk-ant-...")
        anthropic_form.addWidget(self.anthropic_key_input)
        
        anthropic_model = QComboBox()
        anthropic_model.addItems([
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229"
        ])
        anthropic_form.addWidget(anthropic_model)
        self.anthropic_model = anthropic_model
        
        add_anthropic_btn = QPushButton("Add to Team")
        add_anthropic_btn.clicked.connect(lambda: self._quick_add_api("anthropic"))
        anthropic_form.addWidget(add_anthropic_btn)
        
        anthropic_layout.addLayout(anthropic_form)
        anthropic_group.setLayout(anthropic_layout)
        layout.addWidget(anthropic_group)
        
        # Google
        google_group = QGroupBox("Google Gemini")
        google_layout = QVBoxLayout()
        
        google_form = QHBoxLayout()
        google_form.addWidget(QLabel("API Key:"))
        self.google_key_input = QLineEdit()
        self.google_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.google_key_input.setPlaceholderText("AIza...")
        google_form.addWidget(self.google_key_input)
        
        google_model = QComboBox()
        google_model.addItems([
            "gemini-2.0-flash-exp",
            "gemini-1.5-pro",
            "gemini-1.5-flash"
        ])
        google_form.addWidget(google_model)
        self.google_model = google_model
        
        add_google_btn = QPushButton("Add to Team")
        add_google_btn.clicked.connect(lambda: self._quick_add_api("google"))
        google_form.addWidget(add_google_btn)
        
        google_layout.addLayout(google_form)
        google_group.setLayout(google_layout)
        layout.addWidget(google_group)
        
        # Grok
        grok_group = QGroupBox("xAI Grok")
        grok_layout = QVBoxLayout()
        
        grok_form = QHBoxLayout()
        grok_form.addWidget(QLabel("API Key:"))
        self.grok_key_input = QLineEdit()
        self.grok_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.grok_key_input.setPlaceholderText("xai-...")
        grok_form.addWidget(self.grok_key_input)
        
        grok_model = QComboBox()
        grok_model.addItems(["grok-beta", "grok-2-latest"])
        grok_form.addWidget(grok_model)
        self.grok_model = grok_model
        
        add_grok_btn = QPushButton("Add to Team")
        add_grok_btn.clicked.connect(lambda: self._quick_add_api("grok"))
        grok_form.addWidget(add_grok_btn)
        
        grok_layout.addLayout(grok_form)
        grok_group.setLayout(grok_layout)
        layout.addWidget(grok_group)
        
        layout.addStretch()
    
    def _load_team(self):
        """Load current team into table."""
        members = self.team.list_members()
        
        self.team_table.setRowCount(len(members))
        
        for row, config in enumerate(members):
            # Enabled checkbox
            enabled_check = QCheckBox()
            enabled_check.setChecked(config.enabled)
            enabled_check.stateChanged.connect(
                lambda state, id=config.id: self._toggle_enabled(id, state == Qt.CheckState.Checked)
            )
            self.team_table.setCellWidget(row, 0, enabled_check)
            
            # Primary radio
            primary_check = QCheckBox()
            primary_check.setChecked(self.team._primary_id == config.id)
            primary_check.stateChanged.connect(
                lambda state, id=config.id: self._set_primary(id, state == Qt.CheckState.Checked)
            )
            self.team_table.setCellWidget(row, 1, primary_check)
            
            # Name
            self.team_table.setItem(row, 2, QTableWidgetItem(config.name))
            
            # Provider
            self.team_table.setItem(row, 3, QTableWidgetItem(config.provider.value))
            
            # Model
            self.team_table.setItem(row, 4, QTableWidgetItem(config.model))
            
            # Speed tier
            self.team_table.setItem(row, 5, QTableWidgetItem(config.speed_tier))
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            
            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda checked, id=config.id: self._edit_member(id))
            actions_layout.addWidget(edit_btn)
            
            self.team_table.setCellWidget(row, 6, actions_widget)
    
    def _start_discovery(self):
        """Start network discovery."""
        subnet = self.subnet_input.text()
        
        self.discovery_progress.setVisible(True)
        self.discovery_progress.setRange(0, 0)  # Indeterminate
        
        self.discovery_thread = DiscoveryThread(subnet)
        self.discovery_thread.finished.connect(self._on_discovery_finished)
        self.discovery_thread.start()
    
    def _on_discovery_finished(self, endpoints: List[Dict[str, Any]]):
        """Handle discovery completion."""
        self.discovery_progress.setVisible(False)
        self.discovered_endpoints = endpoints
        
        self.discovered_table.setRowCount(len(endpoints))
        
        for row, endpoint in enumerate(endpoints):
            self.discovered_table.setItem(row, 0, QTableWidgetItem(endpoint["hostname"]))
            self.discovered_table.setItem(row, 1, QTableWidgetItem(endpoint["ip"]))
            
            models_str = ", ".join(endpoint["models"][:3])
            if len(endpoint["models"]) > 3:
                models_str += f" (+{len(endpoint['models']) - 3} more)"
            self.discovered_table.setItem(row, 2, QTableWidgetItem(models_str))
            
            # Add button
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            
            add_btn = QPushButton("Add Models")
            add_btn.clicked.connect(lambda checked, ep=endpoint: self._add_from_discovered(ep))
            actions_layout.addWidget(add_btn)
            
            self.discovered_table.setCellWidget(row, 3, actions_widget)
        
        QMessageBox.information(
            self,
            "Discovery Complete",
            f"Found {len(endpoints)} Ollama endpoint(s) with models."
        )
    
    def _add_from_discovered(self, endpoint: Dict[str, Any]):
        """Add models from discovered endpoint."""
        # TODO: Show dialog to select which models to add
        # For now, just add the first model
        if endpoint["models"]:
            config = LLMConfig(
                id=f"ollama_{endpoint['hostname']}_{endpoint['models'][0]}".replace(":", "_"),
                name=f"{endpoint['hostname']} - {endpoint['models'][0]}",
                provider=ProviderType.OLLAMA,
                model=endpoint["models"][0],
                endpoint=endpoint["endpoint"],
                speed_tier="fast" if "3b" in endpoint["models"][0] else "medium",
                cost_tier="free"
            )
            
            self.team.add_member(config)
            self._save_and_refresh()
    
    def _quick_add_api(self, provider: str):
        """Quick add an API provider."""
        if provider == "openai":
            key = self.openai_key_input.text().strip()
            model = self.openai_model.currentText()
            
            if not key:
                QMessageBox.warning(self, "Missing Key", "Please enter your OpenAI API key.")
                return
            
            config = LLMConfig(
                id=f"openai_{model}",
                name=f"OpenAI {model}",
                provider=ProviderType.OPENAI,
                model=model,
                api_key=key,
                speed_tier="medium" if "mini" in model else "slow",
                cost_tier="low" if "mini" in model or "3.5" in model else "high"
            )
            
        elif provider == "anthropic":
            key = self.anthropic_key_input.text().strip()
            model = self.anthropic_model.currentText()
            
            if not key:
                QMessageBox.warning(self, "Missing Key", "Please enter your Anthropic API key.")
                return
            
            config = LLMConfig(
                id=f"anthropic_{model}",
                name=f"Claude {model}",
                provider=ProviderType.ANTHROPIC,
                model=model,
                api_key=key,
                speed_tier="fast" if "haiku" in model else "medium",
                cost_tier="medium"
            )
        
        elif provider == "google":
            key = self.google_key_input.text().strip()
            model = self.google_model.currentText()
            
            if not key:
                QMessageBox.warning(self, "Missing Key", "Please enter your Google API key.")
                return
            
            config = LLMConfig(
                id=f"google_{model}",
                name=f"Gemini {model}",
                provider=ProviderType.GOOGLE,
                model=model,
                api_key=key,
                speed_tier="fast" if "flash" in model else "medium",
                cost_tier="free" if "flash" in model else "low"
            )
        
        elif provider == "grok":
            key = self.grok_key_input.text().strip()
            model = self.grok_model.currentText()
            
            if not key:
                QMessageBox.warning(self, "Missing Key", "Please enter your xAI API key.")
                return
            
            config = LLMConfig(
                id=f"grok_{model}",
                name=f"Grok {model}",
                provider=ProviderType.GROK,
                model=model,
                api_key=key,
                speed_tier="medium",
                cost_tier="medium"
            )
        
        else:
            return
        
        self.team.add_member(config)
        self._save_and_refresh()
    
    def _toggle_enabled(self, llm_id: str, enabled: bool):
        """Toggle member enabled state."""
        if llm_id in self.team.configs:
            self.team.configs[llm_id].enabled = enabled
            self._save_team()
    
    def _set_primary(self, llm_id: str, is_primary: bool):
        """Set member as primary."""
        if is_primary:
            self.team.set_primary(llm_id)
            self._save_and_refresh()
    
    def _add_member_dialog(self):
        """Show dialog to add a custom member."""
        # TODO: Implement full add member dialog
        QMessageBox.information(
            self,
            "Add Member",
            "Use the 'Discover Ollama' or 'Add API Provider' tabs to add team members."
        )
    
    def _edit_member(self, llm_id: str):
        """Edit a team member."""
        # TODO: Implement edit dialog
        QMessageBox.information(self, "Edit", f"Edit functionality for {llm_id} coming soon.")
    
    def _remove_selected(self):
        """Remove selected team member."""
        current_row = self.team_table.currentRow()
        if current_row >= 0:
            members = self.team.list_members()
            if current_row < len(members):
                config = members[current_row]
                
                reply = QMessageBox.question(
                    self,
                    "Remove Member",
                    f"Remove {config.name} from the team?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.team.remove_member(config.id)
                    self._save_and_refresh()
    
    def _test_all(self):
        """Test all team members."""
        # TODO: Run async test
        QMessageBox.information(self, "Test", "Testing all team members...")
    
    def _warmup_all(self):
        """Warm up all team members."""
        # TODO: Run async warmup
        QMessageBox.information(self, "Warm Up", "Warming up all team members...")
    
    def _save_team(self):
        """Save team to preferences."""
        self.prefs.llm_team = self.team.to_dict()
        self.prefs.save()
        self.team_updated.emit()
    
    def _save_and_refresh(self):
        """Save and refresh the display."""
        self._save_team()
        self._load_team()
