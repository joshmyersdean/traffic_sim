import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation
import numpy as np
from entities.car import Car
from utils.visualization import setup_visualization, update_visualization
from models.neural_network import NeuralNetworkModel

class TrafficSimulation:
    def __init__(self, traffic_model, traffic_generator, config):
        self.model = traffic_model
        self.traffic = traffic_generator
        self.config = config
        self.time_step = 0
        self.queues = {d: {l: [] for l in config.spawn_lane_types} for d in config.directions}
        self.active_cars = []
        self.collision_count = 0
        
        self._visualization_initialized = False
        self.fig = None
        self.ax = None
        self.scat = None
        self.light_patches = None

    def _init_visualization(self):
        """Initialize visualization components if not already initialized"""
        if not self._visualization_initialized:
            self.fig, self.ax, self.scat, self.light_patches, self.text_counters = setup_visualization(self.config) # Unpack text_counters as well
            self._visualization_initialized = True

    def update(self, frame):
        self.time_step += 1
        self.traffic.spawn_cars(self.time_step, self.queues)

        collision_detected = self._check_collisions()

        if isinstance(self.model, NeuralNetworkModel):
            state = self.model.get_state(self.queues)

        light_state = self.model.get_light_state(self.time_step, self.queues)
        allowed_dirs = ['N', 'S'] if light_state[0] == 'NS' else ['E', 'W']

        self._process_movements(light_state, allowed_dirs)

        if isinstance(self.model, NeuralNetworkModel):
            self.model.update_car_positions(self.active_cars)
            self.model.update_wait_times(self.queues, light_state, self.time_step)
            reward, avg_wait = self.model.calculate_reward(self.queues, light_state, self.active_cars) # Unpack the tuple
            next_state = self.model.get_state(self.queues)
            done = False
            self.model.remember(state, self._light_state_to_action(light_state),
                                reward, next_state, done) # Pass only the reward
            self.model.replay()
            self.model.cleanup_wait_times(self.active_cars, self.queues)

        if self._visualization_initialized:
            update_visualization(
                self.ax, self.scat, self.light_patches,
                self.active_cars, light_state, allowed_dirs,
                self.time_step, self.config,
                self.queues, self.text_counters 
            )
    
    def run(self):
        """Run with visualization"""
        self._init_visualization()
        
        anim = animation.FuncAnimation(
            self.fig, 
            self.update, 
            interval=500,
            cache_frame_data=False,
            save_count=1000
        )
        plt.show()
    
    def run_headless(self, steps=1000):
        """Run without visualization"""
        for _ in range(steps):
            self.update(None)

    def _light_state_to_action(self, light_state):
        """Convert light state to action index"""
        if light_state == ('NS', 'left'):
            return 0
        elif light_state == ('NS', 'straight'):
            return 1
        elif light_state == ('EW', 'left'):
            return 2
        else:
            return 3
        
    def _process_movements(self, light_state, allowed_dirs):
        light_dir, light_lane = light_state
        
        for d in allowed_dirs:
            if light_lane == 'left' and self.queues[d]['left']:
                self.active_cars.append(self.queues[d]['left'].pop(0))
            elif light_lane == 'straight':
                if self.queues[d]['straight_forward']:
                    self.active_cars.append(self.queues[d]['straight_forward'].pop(0))
                if self.queues[d]['right']:
                    self.active_cars.append(self.queues[d]['right'].pop(0))
        
        remaining_cars = []
        for car in self.active_cars:
            car.move()
            if not car.finished:
                remaining_cars.append(car)
        self.active_cars = remaining_cars

    def _check_collisions(self):
        """Check for cars that are too close and moving in different directions"""
        collision_detected = False
        
        for i, car1 in enumerate(self.active_cars):
            for j, car2 in enumerate(self.active_cars[i+1:], i+1):
                # Check distance threshold
                distance = np.linalg.norm(car1.position - car2.position)
                if distance < self.config.collision_threshold:
                    # Check if cars are moving in significantly different directions
                    angle_diff = self._get_angle_difference(car1.cardinal_direction, car2.cardinal_direction)
                    
                    # Only consider it a collision if directions differ by more than 45 degrees
                    if angle_diff > 45:
                        print(f"Collision detected at timestep {self.time_step}:")
                        print(f"- Car from {car1.origin} moving {car1.cardinal_direction} at {car1.position}")
                        print(f"- Car from {car2.origin} moving {car2.cardinal_direction} at {car2.position}")
                        print(f"Distance: {distance:.2f}, Angle difference: {angle_diff:.1f}°")
                        self.collision_count += 1
                        collision_detected = True
                        
        return collision_detected

    def _get_angle_difference(self, dir1, dir2):
        """Calculate angle between two cardinal directions (N,S,E,W)"""
        directions = {'N': 90, 'S': 270, 'E': 0, 'W': 180}
        angle1 = directions.get(dir1, 0)
        angle2 = directions.get(dir2, 0)
        diff = abs(angle1 - angle2)
        
        return min(diff, 360 - diff)  # Get smallest angle difference
