from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter
from PyQt6.QtCore import Qt, QTimer

from services.project_service import ProjectService
from services.docker_service import DockerService
from services.git_service import GitService
from views.project_panel import ProjectPanel
from views.docker_panel import DockerPanel
from views.git_panel import GitPanel
from utils.debug import debug_print

class DevSupportApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dev-Support (MVC)")
        self.setGeometry(100, 100, 1280, 600)
        
        # Initialize services
        debug_print("Initializing services")
        self.project_service = ProjectService()
        self.docker_service = DockerService()
        
        # Test Git service
        debug_print("Testing Git service in app initialization")
        self.git_service = GitService()
        
        # Create UI
        debug_print("Creating UI")
        self.create_ui()
        
        debug_print("Application initialized")
    
    def create_ui(self):
        """Create the main user interface"""
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        
        # Create a splitter for the project panel and the right side panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)  # Prevent sections from collapsing
        
        # Create project panel with fixed width
        debug_print("Creating project panel")
        self.project_panel = ProjectPanel(self.project_service)
        self.project_panel.setMinimumWidth(550)
        self.project_panel.setMaximumWidth(550)  # Set maximum width to make it fixed
        
        # Create right side container widget
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create Docker panel
        debug_print("Creating docker panel")
        self.docker_panel = DockerPanel(self.docker_service)
        
        # Create Git panel
        debug_print("Creating git panel")
        self.git_panel = GitPanel(self.project_service)
        
        # Add panels to right layout
        right_layout.addWidget(self.docker_panel)
        right_layout.addWidget(self.git_panel)
        
        # Add panels to splitter
        splitter.addWidget(self.project_panel)
        splitter.addWidget(right_widget)
        
        # Set initial sizes for the splitter
        splitter.setSizes([550, 730])
        
        # Add splitter to main layout
        main_layout.addWidget(splitter)
        
        # Set main widget as central widget
        self.setCentralWidget(main_widget)
        
        # Connect project selection to Git panel update
        self.project_panel.project_dropdown.currentIndexChanged.connect(self.update_git_panel)
        
        debug_print("UI creation complete")
        
        # Manually trigger Git panel update for the initial project selection
        # Use a short delay to ensure all UI elements are properly initialized
        QTimer.singleShot(100, self.initial_git_panel_update)
    
    def update_git_panel(self):
        """Update Git panel when project selection changes"""
        current_index = self.project_panel.project_dropdown.currentIndex()
        if current_index >= 0 and current_index < len(self.project_service.projects):
            project = self.project_service.projects[current_index]
            self.git_panel.update_for_project(project)
    
    def initial_git_panel_update(self):
        """Initialize Git panel with the initially selected project"""
        debug_print("Performing initial Git panel update")
        self.update_git_panel()  # This will update the Git panel for the currently selected project
