from entities.intersection import IntersectionConfig
from models.fixed_cycle import FixedCycleModel
from traffic.random_traffic import RandomTrafficGenerator
from simulation import TrafficSimulation
from models.neural_network import NeuralNetworkModel 

def train_headless(config, episodes=10, steps_per_episode=1000):
    """Train the neural network without visualization"""
    model = NeuralNetworkModel(config)
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
    
    # Run with a neural network model - still needs a lot of tuning
    #trained_model = train_headless(config, episodes=10, steps_per_episode=1000)
    #run_with_visualization(config, trained_model)

    # Run with a fixed cycle (ie: traffic light switches every few seconds)
    fixed_cycle_model = FixedCycleModel(config) 
    run_with_visualization(config, fixed_cycle_model)

if __name__ == "__main__":
    main()