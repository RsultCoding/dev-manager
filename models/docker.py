class DockerContainer:
    def __init__(self, container_id, name, image, status, ports):
        self.container_id = container_id
        self.name = name
        self.image = image
        self.status = status
        self.ports = ports

class DockerImage:
    def __init__(self, repository, tag, image_id, created, size):
        self.repository = repository
        self.tag = tag
        self.image_id = image_id
        self.created = created
        self.size = size 