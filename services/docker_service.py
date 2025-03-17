import subprocess
from models.docker import DockerContainer, DockerImage
from utils.debug import debug_print
from config import SUBPROCESS_TIMEOUT

class DockerService:
    def __init__(self):
        self.containers = []
        self.images = []
    
    def check_docker_available(self):
        """Check if Docker is available on the system"""
        try:
            result = subprocess.run(
                ["docker", "info"], 
                capture_output=True, 
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def get_containers(self):
        """Get list of Docker containers"""
        self.containers = []
        
        try:
            debug_print("Running docker ps --all command...")
            
            # Use a simpler format string to ensure consistent parsing
            result = subprocess.run(
                ["docker", "ps", "--all", "--no-trunc"],
                capture_output=True,
                text=True,
                timeout=SUBPROCESS_TIMEOUT
            )
            
            debug_print(f"Docker command return code: {result.returncode}")
            
            if result.returncode == 0:
                # Skip header line
                lines = result.stdout.strip().split('\n')[1:] if result.stdout.strip() else []
                debug_print(f"Number of container lines found: {len(lines)}")
                
                for line in lines:
                    if not line.strip():
                        continue
                        
                    # Split by multiple spaces to parse docker ps output
                    parts = [part for part in line.split('   ') if part.strip()]
                    debug_print(f"Raw container parts: {parts}")
                    
                    if len(parts) >= 4:  # At minimum we need ID, Image, Status, Names
                        # Parse the container info - standard docker ps format has these columns:
                        # CONTAINER ID, IMAGE, COMMAND, CREATED, STATUS, PORTS, NAMES
                        container_id = parts[0].strip()
                        image = parts[1].strip()
                        
                        # Status is typically the 4th or 5th column depending on format
                        status_index = 4 if len(parts) >= 6 else 3
                        status = parts[status_index].strip() if status_index < len(parts) else "Unknown"
                        
                        # Name is the last column
                        name = parts[-1].strip()
                        
                        # Ports might be empty for stopped containers
                        ports = parts[5].strip() if len(parts) > 5 else ""
                        
                        container = DockerContainer(
                            container_id=container_id,
                            name=name,
                            image=image,
                            status=status,
                            ports=ports
                        )
                        
                        self.containers.append(container)
                        debug_print(f"Added container: {container.name}, status: {container.status}")
                    else:
                        debug_print(f"Skipping container line with insufficient parts: {line}")
                
                debug_print(f"Total containers found: {len(self.containers)}")
            else:
                debug_print(f"Docker ps command failed with error: {result.stderr}")
            
            return result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            debug_print("Docker containers command timed out")
            return "ERROR: Command timed out"
        except Exception as e:
            debug_print(f"Error getting Docker containers: {str(e)}")
            return f"ERROR: {str(e)}"
    
    def get_images(self):
        """Get list of Docker images"""
        self.images = []
        
        try:
            result = subprocess.run(
                ["docker", "images", "--format", "{{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.CreatedAt}}\t{{.Size}}"],
                capture_output=True,
                text=True,
                timeout=SUBPROCESS_TIMEOUT
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line:
                        parts = line.split('\t')
                        if len(parts) >= 5:
                            image = DockerImage(
                                repository=parts[0],
                                tag=parts[1],
                                image_id=parts[2],
                                created=parts[3],
                                size=parts[4]
                            )
                            self.images.append(image)
            
            return result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            debug_print("Docker images command timed out")
            return "ERROR: Command timed out"
        except Exception as e:
            debug_print(f"Error getting Docker images: {str(e)}")
            return f"ERROR: {str(e)}" 