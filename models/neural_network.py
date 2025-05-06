import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import random
import itertools
from collections import defaultdict

class NeuralNetworkModel:
    def __init__(self, config):
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.reward_params = {
            'collision_penalty_weight': -5,
            'throughput_bonus_weight': 1.0,
            'min_green_time': 5,
            'duration_reward_decay': 1.0,
            'active_queue_weight': 0.2,
            'imbalance_penalty_weight': -0.1
        }

        # Neural Network
        self.state_size = len(config.directions) * len(config.spawn_lane_types)
        self.action_size = 4  # NS-left, NS-straight, EW-left, EW-straight
        self.model = self._build_model()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        
        # Tracking and memory
        self.wait_times = {}     
        self.memory = deque(maxlen=2000)
        self.batch_size = 32
        self.gamma = 0.95

        # Exploration parameters - uses greedy epsilon. This was not tuned extensively 
        self.epsilon = 1.0       # Initial exploration rate
        self.epsilon_min = 0.01  # Minimum exploration rate
        self.epsilon_decay = 0.995  # Decay rate per episode
        self.exploration_decay_steps = 1000  # Steps before epsilon reaches min
        self.steps_done = 0
        
        # To ensure the model doesn't switch lights too quickly
        self.current_green_duration = 0
        self.last_light_state = None
        self.min_green_time = 5  # Minimum timesteps before switching

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
    
    def get_light_state(self, time_step, queues):
        state = self.get_state(queues)
        
        # Epsilon-greedy action selection
        if random.random() < self.epsilon:
            action = random.randint(0, self.action_size - 1)
        else:
            with torch.no_grad():
                action_values = self.model(state)
            action = torch.argmax(action_values).item()
        
        # Update exploration rate
        self._decay_epsilon()
        
        # Map action to light state
        if action == 0:
            return ('NS', 'left')
        elif action == 1:
            return ('NS', 'straight')
        elif action == 2:
            return ('EW', 'left')
        else:
            return ('EW', 'straight')
    
    def _decay_epsilon(self):
        """Decay epsilon over time"""
        self.steps_done += 1
        self.epsilon = max(self.epsilon_min, 
                          self.epsilon * self.epsilon_decay)
    
    def reset_epsilon(self, value=1.0):
        """Reset epsilon for new training runs"""
        self.epsilon = value
        self.steps_done = 0
    
    def get_state(self, queues):
        """Convert queue lengths to state vector"""
        state = []
        for direction in self.config.directions:
            for lane in self.config.spawn_lane_types:
                state.append(len(queues[direction][lane]))
        return torch.FloatTensor(state).to(self.device)
    
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

    def calculate_reward(self, queues, light_state, collision_detected=False, previous_queues=None):
        try:
            # Track light duration
            if light_state == self.last_light_state:
                self.current_green_duration += 1
            else:
                self.current_green_duration = 1
            self.last_light_state = light_state

            # 1. Collision penalty
            collision_penalty = self.reward_params['collision_penalty_weight'] if collision_detected else 0
            
            # 2. Queue-based rewards
            direction_counts = {d: 0 for d in self.config.directions}
            for direction in self.config.directions:
                for lane in self.config.spawn_lane_types:
                    direction_counts[direction] += len(queues[direction][lane])
            
            # 3. Active direction metrics
            active_dir = light_state[0]
            active_queue = direction_counts['N'] + direction_counts['S'] if active_dir == 'NS' else direction_counts['E'] + direction_counts['W']
            inactive_queue = direction_counts['E'] + direction_counts['W'] if active_dir == 'NS' else direction_counts['N'] + direction_counts['S']
            
            # 4. Throughput calculation
            throughput_bonus = 0
            if previous_queues is not None:
                exited = self.count_queue_exit(previous_queues, queues, light_state)
                throughput_bonus = exited * self.reward_params['throughput_bonus_weight']
            
            # 5. Dynamic rewards based on duration
            duration_reward = 0
            if self.current_green_duration < self.reward_params['min_green_time']:
                # Penalize switching too soon
                duration_reward = -2.0
            elif self.current_green_duration > self.reward_params['min_green_time']:
                # Decaying reward for staying green
                duration_reward = (active_queue * self.reward_params['active_queue_weight']) * \
                                 (self.reward_params['duration_reward_decay'] ** (self.current_green_duration - self.reward_params['min_green_time']))
            
            # 6. Queue imbalance penalty
            imbalance_penalty = self.reward_params['imbalance_penalty_weight'] * (inactive_queue - active_queue) if inactive_queue > active_queue else 0
            
            # Combined reward
            reward = (
                collision_penalty +
                throughput_bonus +
                duration_reward +
                imbalance_penalty
            )
            
            return reward, sum(direction_counts.values()) / len(direction_counts)

        except KeyError as e:
            print(f"KeyError in calculate_reward: {e}")
            return 0, 0

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
    
    def replay(self):
        if len(self.memory) < self.batch_size:
            return

        minibatch = random.sample(self.memory, self.batch_size)
        states = torch.stack([x[0] for x in minibatch]).to(self.device)
        actions = torch.tensor([x[1] for x in minibatch], dtype=torch.long).to(self.device)
        rewards = torch.tensor([x[2] for x in minibatch], dtype=torch.float32).to(self.device).squeeze()
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
                    cleaned_wait_times[car_id] = {
                        'first_seen': wait_data.get('first_seen', 0),
                        'last_moved': wait_data.get('last_moved', 0),
                        'total_wait': wait_data.get('total_wait', 0)
                    }
            
            self.wait_times = cleaned_wait_times
        
        except Exception as e:
            print(f"Error in cleanup_wait_times: {e}")

    def count_queue_exit(self, queues_before, queues_after, light_state):
        light_dir, _ = light_state
        directions = ['N', 'S'] if light_dir == 'NS' else ['E', 'W']
        exited = 0
        for d in directions:
            for lane in queues_before[d]:
                before = len(queues_before[d][lane])
                after = len(queues_after[d][lane])
                if before > after:
                    exited += before - after
        return exited