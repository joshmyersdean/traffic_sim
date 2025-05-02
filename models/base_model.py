class BaseTrafficLightModel:
    def __init__(self, config):
        self.config = config
    
    def get_light_state(self, time_step, queues):
        """To be implemented by child classes"""
        raise NotImplementedError
        
    def update(self, time_step, queues):
        """Optional method for models that need to learn/update"""
        pass