from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QSplitter
from PyQt6.QtCore import Qt

from services.project_service import ProjectService
from services.docker_service import DockerService
from views.project_panel import ProjectPanel
from views.docker_panel import DockerPanel
from utils.debug import debug_print

class DevSupportApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dev-Support (MVC)")
        self.setGeometry(100, 100, 1280, 600)
        
        # Initialize services
        self.project_service = ProjectService()
        self.docker_service = DockerService()
        
        # Create UI
        self.create_ui()
        
        debug_print("Application initialized")
    
    def create_ui(self):
        """Create the main user interface"""
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        
        # Create a splitter for the two main sections
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)  # Prevent sections from collapsing
        
        # Create project panel with fixed width
        self.project_panel = ProjectPanel(self.project_service)
        self.project_panel.setMinimumWidth(550)
        self.project_panel.setMaximumWidth(550)  # Set maximum width to make it fixed
        
        # Create Docker panel with flexible width but default size
        self.docker_panel = DockerPanel(self.docker_service)
        self.docker_panel.setMinimumWidth(600)
        
        # Add panels to splitter
        splitter.addWidget(self.project_panel)
        splitter.addWidget(self.docker_panel)
        
        # Set initial sizes for the splitter
        splitter.setSizes([550, 730])
        
        # Add splitter to main layout
        main_layout.addWidget(splitter)
        
        # Set the main widget
        self.setCentralWidget(main_widget)
