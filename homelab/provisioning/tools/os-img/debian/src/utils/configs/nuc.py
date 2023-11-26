from utils.models.config import Config

class NucConfig(Config):
    def __init__(self):
        super().__init__(self)
        self.hostname = 'nuc'
