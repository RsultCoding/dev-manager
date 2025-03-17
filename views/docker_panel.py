from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView
)
from utils.debug import debug_print

class DockerPanel(QWidget):
    def __init__(self, docker_service):
        super().__init__()
        self.docker_service = docker_service
        self.create_ui()
    
    def create_ui(self):
        """Create the Docker panel UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)  # Reduce default spacing between elements
        layout.setContentsMargins(20, 20, 20, 20)  # Set consistent margins
        
        # Panel title
        title = QLabel("Docker Management")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Add some spacing after title
        title_spacing = QWidget()
        title_spacing.setFixedHeight(10)
        layout.addWidget(title_spacing)
        
        # Docker buttons
        btn_frame = QWidget()
        btn_layout = QHBoxLayout(btn_frame)
        btn_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins around buttons
        
        # Container button
        self.container_button = QPushButton("Check All Docker Containers")
        self.container_button.clicked.connect(self.check_containers)
        btn_layout.addWidget(self.container_button)
        
        # Images button
        self.images_button = QPushButton("List Docker Images")
        self.images_button.clicked.connect(self.list_images)
        btn_layout.addWidget(self.images_button)
        
        btn_layout.addStretch()
        layout.addWidget(btn_frame)
        
        # Output section - only show when needed
        self.output_label = QLabel("Docker Output:")
        layout.addWidget(self.output_label)
        
        # Text output for general messages
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setStyleSheet("background-color: #f0f0f0;")
        self.output_text.setMaximumHeight(100)  # Limit height for status messages
        self.output_text.setVisible(False)  # Hide initially
        layout.addWidget(self.output_text)
        
        # Table for containers
        self.containers_table = QTableWidget()
        self.containers_table.setColumnCount(4)
        self.containers_table.setHorizontalHeaderLabels(["CONTAINER ID", "IMAGE", "STATUS", "NAME"])
        
        # Configure container table columns
        container_header = self.containers_table.horizontalHeader()
        container_header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        container_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Image
        container_header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Status
        container_header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Name
        
        # Ensure the table uses all available horizontal space
        self.containers_table.horizontalHeader().setStretchLastSection(True)
        self.containers_table.setVisible(False)  # Hide initially
        layout.addWidget(self.containers_table)
        
        # Table for images
        self.images_table = QTableWidget()
        self.images_table.setColumnCount(5)
        self.images_table.setHorizontalHeaderLabels(["REPOSITORY", "TAG", "IMAGE ID", "CREATED", "SIZE"])
        
        # Configure images table columns
        image_header = self.images_table.horizontalHeader()
        image_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Repository
        image_header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Tag
        image_header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # ID
        image_header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Created
        image_header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Size
        
        # Ensure the table uses all available horizontal space
        self.images_table.horizontalHeader().setStretchLastSection(True)
        self.images_table.setVisible(False)  # Hide initially
        layout.addWidget(self.images_table)
        
        # Add stretch at the end to push everything to the top
        layout.addStretch()
    
    def check_containers(self):
        """Check Docker containers and display results"""
        # Show output elements
        self.output_label.setVisible(True)
        self.output_text.setVisible(True)
        self.containers_table.setVisible(True)
        self.images_table.setVisible(False)
        
        # Clear existing output
        self.output_text.clear()
        self.output_text.append("Checking all Docker containers (running and stopped)...")
        
        # Check if Docker is available
        if not self.docker_service.check_docker_available():
            self.output_text.append("ERROR: Docker is not available. Please ensure Docker is running.")
            self.containers_table.setVisible(False)
            return
        
        # Get containers
        output = self.docker_service.get_containers()
        
        # Format container output
        if self.docker_service.containers:
            # Clear existing rows
            self.containers_table.setRowCount(0)
            
            # Group containers by running status
            running_containers = []
            stopped_containers = []
            
            for container in self.docker_service.containers:
                if container.status.lower().startswith("up"):
                    running_containers.append(container)
                else:
                    stopped_containers.append(container)
            
            # Display running containers first with green background
            row = 0
            for container in running_containers:
                self.containers_table.insertRow(row)
                
                id_item = QTableWidgetItem(container.container_id[:12])
                image_item = QTableWidgetItem(container.image)
                status_item = QTableWidgetItem(container.status)
                name_item = QTableWidgetItem(container.name)
                
                # Set green background for running containers
                for item in [id_item, image_item, status_item, name_item]:
                    item.setBackground(QTableWidget().palette().color(QTableWidget.Palette.Role.AlternateBase))
                
                self.containers_table.setItem(row, 0, id_item)
                self.containers_table.setItem(row, 1, image_item)
                self.containers_table.setItem(row, 2, status_item)
                self.containers_table.setItem(row, 3, name_item)
                
                row += 1
            
            # Display stopped containers
            for container in stopped_containers:
                self.containers_table.insertRow(row)
                
                self.containers_table.setItem(row, 0, QTableWidgetItem(container.container_id[:12]))
                self.containers_table.setItem(row, 1, QTableWidgetItem(container.image))
                self.containers_table.setItem(row, 2, QTableWidgetItem(container.status))
                self.containers_table.setItem(row, 3, QTableWidgetItem(container.name))
                
                row += 1
            
            # Update status message
            self.output_text.append(f"Total: {len(self.docker_service.containers)} containers "
                                   f"({len(running_containers)} running, {len(stopped_containers)} stopped)")
        else:
            self.output_text.append("No Docker containers found (running or stopped).")
            self.containers_table.setVisible(False)
            if output and "ERROR" in output:
                self.output_text.append(output)
    
    def list_images(self):
        """List Docker images in a table"""
        # Show/hide appropriate elements
        self.output_label.setVisible(True)
        self.output_text.setVisible(True)
        self.containers_table.setVisible(False)
        self.images_table.setVisible(True)
        
        # Clear existing output
        self.output_text.clear()
        self.output_text.append("Listing Docker images...")
        
        # First check if Docker is available
        if not self.docker_service.check_docker_available():
            self.output_text.append("ERROR: Docker is not available. Please ensure Docker is running.")
            self.images_table.setVisible(False)
            return
        
        # Get images
        output = self.docker_service.get_images()
        
        # Show table if we have images, otherwise show text
        if self.docker_service.images:
            # Clear existing rows
            self.images_table.setRowCount(0)
            
            # Populate table
            for i, image in enumerate(self.docker_service.images):
                self.images_table.insertRow(i)
                self.images_table.setItem(i, 0, QTableWidgetItem(image.repository))
                self.images_table.setItem(i, 1, QTableWidgetItem(image.tag))
                self.images_table.setItem(i, 2, QTableWidgetItem(image.image_id))
                self.images_table.setItem(i, 3, QTableWidgetItem(image.created))
                self.images_table.setItem(i, 4, QTableWidgetItem(image.size))
            
            # Update status message
            self.output_text.append(f"Found {len(self.docker_service.images)} Docker images.")
        else:
            self.output_text.append("No Docker images found.")
            self.images_table.setVisible(False)
            if output and "ERROR" in output:
                self.output_text.append(output) 