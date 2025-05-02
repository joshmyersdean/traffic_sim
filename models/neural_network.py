import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import random

class NeuralNetworkModel:
    def __init__(self, config):
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Neural Network
        self.state_size = len(config.directions) * len(config.spawn_lane_types)  # Queue lengths
        self.action_size = 4  # NS-left, NS-straight, EW-left, EW-straight -> Each light
        self.model = self._build_model()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        
        # Tracking
        self.car_positions = {}  
        self.wait_times = {}     
        self.memory = deque(maxlen=2000)
        self.batch_size = 32
        self.gamma = 0.95

        self.episode_rewards = []
        self.episode_wait_times = []
        
    def _build_model(self):
        model = nn.Sequential(
            nn.Linear(self.state_size, 24),
            nn.ReLU(),
            nn.Linear(24, 24),
            nn.ReLU(),
            nn.Linear(24, self.action_size)
        ).to(self.device)
        return model
    
    def get_state(self, queues):
        """Convert queue lengths to state vector"""
        state = []
        for direction in self.config.directions:
            for lane in self.config.spawn_lane_types:
                state.append(len(queues[direction][lane]))
        return torch.FloatTensor(state).to(self.device)
    
    def get_light_state(self, time_step, queues):
        state = self.get_state(queues)
        with torch.no_grad():
            action_values = self.model(state)
        action = torch.argmax(action_values).item()
        
        # Map action to light state
        if action == 0:
            return ('NS', 'left')
        elif action == 1:
            return ('NS', 'straight')
        elif action == 2:
            return ('EW', 'left')
        else:
            return ('EW', 'straight')
    
    def update_car_positions(self, active_cars):
        """Track all car positions for collision detection"""
        self.car_positions = {id(car): car.position for car in active_cars}
    
    def detect_collisions(self):
        """Check for any cars too close to each other"""
        positions = list(self.car_positions.values())
        for i, pos1 in enumerate(positions):
            for pos2 in positions[i+1:]:
                if np.linalg.norm(pos1 - pos2) < 0.3:  # Collision threshold
                    return True
        return False
    
    def update_wait_times(self, queues, light_state, current_time):
        """Update wait times for all queued cars"""
        try:
            light_dir, _ = light_state
            
            for direction in self.config.directions:
                has_red_light = ((light_dir == 'NS' and direction in ['E', 'W']) or 
                            (light_dir == 'EW' and direction in ['N', 'S']))
                
                for lane in self.config.spawn_lane_types:
                    for car in queues[direction][lane]:
                        car_id = id(car)
                        
                        if car_id not in self.wait_times:
                            self.wait_times[car_id] = {
                                'first_seen': current_time,
                                'last_moved': current_time,
                                'total_wait': 0  
                            }
                        
                        if has_red_light:
                            if self.wait_times[car_id]['last_moved'] == current_time - 1:
                                self.wait_times[car_id]['total_wait'] += 1
                        else:
                            self.wait_times[car_id]['last_moved'] = current_time
    
        except Exception as e:
            print(f"Error in update_wait_times: {e}")
        
    def calculate_reward(self, queues, light_state, active_cars=None):
        """Calculate reward based on current state"""
        try:
            # 1. Collision penalty
            collision_penalty = -100 if self.detect_collisions() else 0
            
            # 2. Wait time penalty (only count cars still in queues)
            current_wait_times = []
            for direction in self.config.directions:
                for lane in self.config.spawn_lane_types:
                    for car in queues[direction][lane]:
                        car_id = id(car)
                        if car_id in self.wait_times:
                            current_wait_times.append(self.wait_times[car_id]['total_wait'])
            
            avg_wait = sum(current_wait_times) / max(1, len(current_wait_times))
            wait_penalty = -avg_wait * 0.05
            
            # 3. Throughput bonus (encourage clearing queues)
            throughput_bonus = 0
            if active_cars is not None:
                throughput_bonus = sum(1 for car in active_cars if car.finished) * 0.5
            
            last_light_state = getattr(self, '_last_light_state', None)
            light_change_reward = 0.01 if last_light_state and light_state != last_light_state else 0
            self._last_light_state = light_state

            reward = collision_penalty + wait_penalty + throughput_bonus + light_change_reward
            return reward, avg_wait
    
        except KeyError as e:
            print(f"KeyError in calculate_reward: {e}")
            print(f"Wait times structure: {self.wait_times}")
            return 0  # Return neutral reward if error occurs
        
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
    
    def replay(self):
        if len(self.memory) < self.batch_size:
            return

        minibatch = random.sample(self.memory, self.batch_size)
        states = torch.stack([x[0] for x in minibatch]).to(self.device)
        actions = torch.tensor([x[1] for x in minibatch], dtype=torch.long).to(self.device)
        rewards = torch.tensor([x[2] for x in minibatch], dtype=torch.float32).to(self.device).squeeze() # Ensure rewards is 1D
        next_states = torch.stack([x[3] for x in minibatch]).to(self.device)
        dones = torch.tensor([x[4] for x in minibatch], dtype=torch.float32).to(self.device).squeeze()

        current_q = self.model(states).gather(1, actions.unsqueeze(1)).squeeze(1)
        with torch.no_grad():
            next_q = self.model(next_states).max(1)[0]

        targets = rewards + (self.gamma * next_q * (1 - dones))

        loss = nn.MSELoss()(current_q, targets)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
            
    def cleanup_wait_times(self, active_cars, queues):
        """Remove entries for cars that have exited the simulation"""
        try:
            active_ids = {id(car) for car in active_cars}
            # Also keep cars that are still in queues
            for direction in self.config.directions:
                for lane in self.config.spawn_lane_types:
                    active_ids.update(id(car) for car in queues[direction][lane])
            
            # Create new dictionary with only active cars
            cleaned_wait_times = {}
            for car_id, wait_data in self.wait_times.items():
                if car_id in active_ids:
                    # Ensure the structure is correct
                    cleaned_wait_times[car_id] = {
                        'first_seen': wait_data.get('first_seen', 0),
                        'last_moved': wait_data.get('last_moved', 0),
                        'total_wait': wait_data.get('total_wait', 0)
                    }
            
            self.wait_times = cleaned_wait_times
        
        except Exception as e:
            print(f"Error in cleanup_wait_times: {e}")