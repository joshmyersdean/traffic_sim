class BaseTrafficGenerator:
    def __init__(self, config):
        self.config = config
        
    def spawn_cars(self, time_step, queues):
        """To be implemented by child classes"""
        raise NotImplementedError