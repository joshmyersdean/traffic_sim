from entities.intersection import IntersectionConfig
from models.fixed_cycle import FixedCycleModel
from traffic.random_traffic import RandomTrafficGenerator
from simulation import TrafficSimulation
from models.neural_network import NeuralNetworkModel 
import itertools
import numpy as np
from collections import defaultdict

def optimize_reward_parameters(config, traffic_generator, param_ranges, num_steps=1000, num_trials=3):
    """
    Optimize reward function parameters by testing different combinations.
    Returns the best parameters found.
    """
    param_names = sorted(param_ranges.keys())
    param_values = [param_ranges[name] for name in param_names]
    param_combinations = list(itertools.product(*param_values))
    
    best_params = None
    best_score = float('inf')
    
    print(f"\nStarting reward parameter optimization with {len(param_combinations)} combinations...")
    
    for i, combination in enumerate(param_combinations):
        params = dict(zip(param_names, combination))
        print(f"\nTesting combination {i+1}/{len(param_combinations)}: {params}")
        
        trial_scores = []
        
        for trial in range(num_trials):
            # Create model with current parameters
            model = NeuralNetworkModel(config)
            
            # Update the model's reward parameters directly
            model.reward_params = params
            
            # Run simulation
            sim = TrafficSimulation(model, traffic_generator, config)
            sim.run_headless(num_steps)
            
            # Calculate performance metrics
            queue_lengths = []
            for direction in config.directions:
                for lane in config.spawn_lane_types:
                    queue_lengths.append(len(sim.queues[direction][lane]))
            
            max_queue = max(queue_lengths)
            std_queue = np.std(queue_lengths)
            score = max_queue + std_queue  # Combine max and std for balanced performance
            
            trial_scores.append(score)
        
        avg_score = np.mean(trial_scores)
        
        if avg_score < best_score:
            best_score = avg_score
            best_params = params.copy()
            best_params['score'] = best_score
            best_params['max_queue'] = max_queue
            best_params['std_queue'] = std_queue
            print(f"New best parameters found! Score: {best_score:.2f}")
    
    print("\nOptimization complete!")
    print(f"Best parameters: {best_params}")
    return best_params

def train_headless(config, reward_params=None, episodes=10, steps_per_episode=1000):
    """Train the neural network without visualization"""
    model = NeuralNetworkModel(config)
    
    # Apply reward parameters if provided
    if reward_params:
        model.reward_params = reward_params
    
    traffic = RandomTrafficGenerator(config)
    sim = TrafficSimulation(model, traffic, config)
    
    print("Starting headless training...")
    for episode in range(episodes):
        sim.run_headless(steps=steps_per_episode)
        print(f"Episode {episode + 1}/{episodes} completed")
        
    print("Training completed!")
    return model

def run_with_visualization(config, trained_model):
    """Run simulation with visualization using trained model"""
    traffic = RandomTrafficGenerator(config)
    sim = TrafficSimulation(trained_model, traffic, config)
    sim.run()

def main():
    config = IntersectionConfig()
    traffic = RandomTrafficGenerator(config)
    
    # Define parameter ranges to optimize
    param_ranges = {
        'collision_penalty_weight': [-10, -5, -2],
        'throughput_bonus_weight': [0.5, 1.0, 2.0],
        'min_green_time': [3, 5, 7],
        'duration_reward_decay': [0.9, 1.0, 1.1],
        'active_queue_weight': [0.1, 0.2, 0.3],
        'imbalance_penalty_weight': [-0.2, -0.1, -0.05]
    }
    
    # Step 1: Optimize reward parameters
    #best_params = optimize_reward_parameters(
    #    config, 
    #    traffic,
    #    param_ranges,
    #    num_steps=500,  # Shorter for optimization
    #    num_trials=2    # Fewer trials for speed
    #)
    
    best_params = {
        'active_queue_weight': 0.2,
        'collision_penalty_weight': -2,
        'duration_reward_decay': 1.0,
        'imbalance_penalty_weight': -0.05,
        'min_green_time': 7,
        'throughput_bonus_weight': 1.0,
    }

    # Step 2: Train with optimized parameters
    print("\nStarting training with optimized parameters...")
    trained_model = train_headless(
        config,
        reward_params=best_params,
        episodes=10,
        steps_per_episode=500
    )
    
    # Step 3: Run visualization with trained model
    run_with_visualization(config, trained_model)
    
    # Optional: Compare with fixed cycle model
    #fixed_cycle_model = FixedCycleModel(config) 
    #run_with_visualization(config, fixed_cycle_model)

if __name__ == "__main__":
    main()