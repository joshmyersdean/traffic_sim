import numpy as np

class Car:
    def __init__(self, origin, lane, config):
        self.origin = origin
        self.lane = lane
        self.config = config
        self.target = config.turn_targets[(origin, lane)]
        self.color = config.shade_colors[(origin, lane)]
        self.finished = False
        self.position = np.array(config.lane_positions[origin][lane], dtype=float)
        self.velocity = np.zeros(2)  # Initialize velocity vector
        self.cardinal_direction = self._get_cardinal_direction()

    def _get_cardinal_direction(self):
        """Determine cardinal direction based on origin"""
        if self.origin == 'N':
            return 'S'  # Moving southward
        elif self.origin == 'S':
            return 'N'  # Moving northward
        elif self.origin == 'E':
            return 'W'  # Moving westward
        else:  # 'W'
            return 'E'  # Moving eastward

    def _mirror_lane(self):
        if self.lane == 'right' or self.lane == 'straight_forward':
            return 'straight_back2'
        return 'straight_back'

    def move(self):
        target_lane = self._mirror_lane()
        try:
            target_pos = np.array(self.config.lane_positions[self.target][target_lane])
            direction = target_pos - self.position
            distance = np.linalg.norm(direction)
            
            # Update velocity vector
            self.velocity = self.config.car_speed * direction / distance if distance > 0 else np.zeros(2)
            
            if distance < self.config.car_speed:
                self.position = target_pos
                self.finished = True
            else:
                self.position += self.velocity
        except KeyError:
            print(f"Error: No target position for {self.origin} {self.lane} -> {self.target} {target_lane}")
            self.finished = True