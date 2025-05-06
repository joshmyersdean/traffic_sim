import random
from .base_traffic import BaseTrafficGenerator
from entities.car import Car

class PatternedTrafficGenerator(BaseTrafficGenerator):
    def __init__(self, config):
        super().__init__(config)
        self.cycle_length = 20  # Pattern repeats every 20 time steps
        self.base_spawn_prob = 0.2
        self.favor_factor = 1.75  # 75% more cars in favored direction
        
    def spawn_cars(self, time_step, queues):
        # Determine which direction to favor in this cycle phase
        cycle_phase = time_step % self.cycle_length
        favored_dir = 'NS' if (time_step // self.cycle_length) % 2 == 0 else 'EW'
        
        for direction in self.config.directions:
            for lane in self.config.spawn_lane_types:
                spawn_prob = self.base_spawn_prob # Base probability

                # Increase probability for favored direction
                if (direction in ['N', 'S'] and favored_dir == 'NS') or \
                   (direction in ['E', 'W'] and favored_dir == 'EW'):
                    spawn_prob *= self.favor_factor
                
                spawn_prob = min(spawn_prob, 0.95)
                
                if random.random() < spawn_prob:
                    queues[direction][lane].append(Car(direction, lane, self.config))