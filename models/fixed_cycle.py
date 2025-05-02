from .base_model import BaseTrafficLightModel

class FixedCycleModel(BaseTrafficLightModel):
    def __init__(self, config):
        super().__init__(config)
        self.green_cycle_duration = 10
        self.left_arrow_duration = 3
        
    def get_light_state(self, time_step, queues):
        cycle_time = (self.green_cycle_duration + self.left_arrow_duration) * 2
        t = time_step % cycle_time
        
        if t < self.left_arrow_duration:
            return ('NS', 'left')
        elif t < self.left_arrow_duration + self.green_cycle_duration:
            return ('NS', 'straight')
        elif t < 2 * self.left_arrow_duration + self.green_cycle_duration:
            return ('EW', 'left')
        else:
            return ('EW', 'straight')