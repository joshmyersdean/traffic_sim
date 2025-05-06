from entities.intersection import IntersectionConfig
from models.fixed_cycle import FixedCycleModel
from traffic.random_traffic import RandomTrafficGenerator
from traffic.pattern_traffic import PatternedTrafficGenerator   
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
            model = NeuralNetworkModel(config)
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
            score = max_queue + std_queue 
            
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
    
    #traffic = RandomTrafficGenerator(config)
    traffic = PatternedTrafficGenerator(config)
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

def evaluate_model_on_single_run(config, model, traffic_generator, num_steps=100):
    """
    Runs a simulation headlessly and returns:
    - Number of cars exited (throughput)
    - Number of collisions
    """
    sim = TrafficSimulation(model, traffic_generator, config)
    sim.run_headless(steps=num_steps)
    return sim.cars_exited, sim.collision_count

def evaluate_model(config, model, traffic_generator, num_steps=100, num_runs=50, crash_penalty=4):
    """
    Runs the simulation multiple times and returns average:
    - Number of cars exited (throughput)
    - Number of collisions
    - Adjusted throughput based on collisions
    """
    total_exited = 0
    total_collisions = 0
    adjusted_exited = 0

    for run in range(num_runs):
        sim = TrafficSimulation(model, traffic_generator, config)
        sim.run_headless(steps=num_steps)

        exited = sim.cars_exited
        collisions = sim.collision_count

        total_exited += exited
        total_collisions += collisions

        cars_per_step = exited / num_steps
        adjusted_exited += exited - (collisions * cars_per_step * crash_penalty)

    avg_exited = total_exited / num_runs
    avg_collisions = total_collisions / num_runs
    avg_adjusted_exited = adjusted_exited / num_runs

    return avg_exited, avg_collisions, avg_adjusted_exited


def main():
    config = IntersectionConfig()
    #traffic = RandomTrafficGenerator(config) # Use random traffic for initial training
    traffic = PatternedTrafficGenerator(config) # Use patterned traffic for initial training - currently set to 75% of cars in the favored direction
    
    # Define parameter ranges to optimize
    param_ranges = {
        'collision_penalty_weight': [-3, -2, -1.5],
        'throughput_bonus_weight': [3.0, 4.0, 4.5],
        'min_green_time': [1.5, 2, 3],
        'duration_reward_decay': [0.9, 1.1, 1.2],
        'active_queue_weight': [0.2, 0.3, 0.4],
        'imbalance_penalty_weight': [-0.25, -0.2, -0.15]
    }
    
    # Optimize reward parameters - uncomment this if you want to test all of the parameter combinations from param_ranges above
    #best_params = optimize_reward_parameters(
    #    config, 
    #    traffic,
    #    param_ranges,
    #    num_steps=100,  # Shorter for optimization
    #    num_trials=2    # Fewer trials for speed
    #)

    best_params = {
        'active_queue_weight': 0.35,
        'collision_penalty_weight': -1.5,
        'duration_reward_decay': 1.2,
        'imbalance_penalty_weight': -0.25,
        'min_green_time': 2.5,
        'throughput_bonus_weight': 1.5,
    }


    # Train with optimized parameters
    print("\nStarting training with optimized parameters...")
    trained_model = train_headless(
        config,
        reward_params=best_params,
        episodes=10,
        steps_per_episode=100
    )
    
    # Test throughput
    print("======= Evaluating Models ======")
    trained_exited, trained_collisions, trained_adjusted = evaluate_model(config, trained_model, traffic, num_steps=100)
    print(f"Trained Model - Throughput: {trained_exited} cars, Collisions: {trained_collisions}, Adjusted Throughput: {trained_adjusted}")

    fixed_model = FixedCycleModel(config)
    fixed_exited, fixed_collisions, fixed_adjusted = evaluate_model(config, fixed_model, traffic, num_steps=100)
    print(f"Fixed-Cycle Model - Throughput: {fixed_exited} cars, Collisions: {fixed_collisions}, Adjusted Throughput: {fixed_adjusted}")


    # Step 3: Run visualization with trained model
    #run_with_visualization(config, trained_model)
    
    #  Run visualization with fixed cycle model
    fixed_cycle_model = FixedCycleModel(config) 
    run_with_visualization(config, fixed_cycle_model)

    
if __name__ == "__main__":
    main()