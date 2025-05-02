import random
from .base_traffic import BaseTrafficGenerator
from entities.car import Car

class RandomTrafficGenerator(BaseTrafficGenerator):
    def spawn_cars(self, time_step, queues):
        for d in self.config.directions:
            for lane in self.config.spawn_lane_types:
                if random.random() < 0.2:
                    queues[d][lane].append(Car(d, lane, self.config))