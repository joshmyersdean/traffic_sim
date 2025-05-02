class IntersectionConfig:
    def __init__(self):
        # Simulation parameters
        self.car_speed = 0.2
        self.collision_threshold = 0.3 
        self.collision_cooldown = 5  # timesteps to ignore same collision

        # Lane positions for each direction (x, y coordinates)
        self.lane_positions = {
            'N': {
                'straight_back': (1.2, 4),    
                'straight_back2': (0.6, 4),
                'right': (0.0, 4),            
                'straight_forward': (-0.6, 4),
                'left': (-1.2, 4)             
            },
            'S': {
                'straight_back': (-1.2, -4),  
                'straight_back2': (-0.6, -4),
                'right': (0.0, -4),         
                'straight_forward': (0.6, -4),
                'left': (1.2, -4)            
            },
            'E': {
                'straight_back': (4, -1.2),   
                'straight_back2': (4, -0.6),
                'right': (4, 0.0),           
                'straight_forward': (4, 0.6),
                'left': (4, 1.2)             
            },
            'W': {
                'straight_back': (-4, 1.2),   
                'straight_back2': (-4, 0.6),
                'right': (-4, 0.0),          
                'straight_forward': (-4, -0.6),
                'left': (-4, -1.2)           
            }
        }
        
        # Direction and lane configuration
        self.directions = ['N', 'E', 'S', 'W']
        self.spawn_lane_types = ['left', 'straight_forward', 'right']  # Lanes that spawn cars
        self.all_lane_types = ['straight_back', 'straight_back2', 'left', 'straight_forward', 'right']  # All lane types
        
        # Mapping of origin lane to target direction
        self.turn_targets = {
            # Northbound turns
            ('N', 'left'): 'W',
            ('N', 'straight_forward'): 'S',
            ('N', 'right'): 'E',
            ('N', 'straight_back'): 'S',
            ('N', 'straight_back2'): 'S',
            
            # Southbound turns
            ('S', 'left'): 'E',
            ('S', 'straight_forward'): 'N',
            ('S', 'right'): 'W',
            ('S', 'straight_back'): 'N',
            ('S', 'straight_back2'): 'N',
            
            # Eastbound turns
            ('E', 'left'): 'N',
            ('E', 'straight_forward'): 'W',
            ('E', 'right'): 'S',
            ('E', 'straight_back'): 'W',
            ('E', 'straight_back2'): 'W',
            
            # Westbound turns
            ('W', 'left'): 'S',
            ('W', 'straight_forward'): 'E',
            ('W', 'right'): 'N',
            ('W', 'straight_back'): 'E',
            ('W', 'straight_back2'): 'E'
        }
        
        # Color coding for different lanes/directions
        self.shade_colors = {
            # Northbound colors
            ('N', 'left'): 'pink',
            ('N', 'straight_forward'): 'red',
            ('N', 'right'): 'lightcoral',
            ('N', 'straight_back'): 'darkred',
            ('N', 'straight_back2'): 'darkred',
            
            # Southbound colors
            ('S', 'left'): 'lightblue',
            ('S', 'straight_forward'): 'blue',
            ('S', 'right'): 'skyblue',
            ('S', 'straight_back'): 'darkblue',
            ('S', 'straight_back2'): 'darkblue',
            
            # Eastbound colors
            ('E', 'left'): 'lightgreen',
            ('E', 'straight_forward'): 'green',
            ('E', 'right'): 'lime',
            ('E', 'straight_back'): 'darkgreen',
            ('E', 'straight_back2'): 'darkgreen',
            
            # Westbound colors
            ('W', 'left'): 'khaki',
            ('W', 'straight_forward'): 'yellow',
            ('W', 'right'): 'gold',
            ('W', 'straight_back'): 'goldenrod',
            ('W', 'straight_back2'): 'goldenrod'
        }
        
        # Traffic light positions (relative to lanes)
        self.light_positions = {
            'N': {
                'left': (-1.0, 4.5),
                'straight': (0.0, 4.5)
            },
            'S': {
                'left': (1.0, -4.5),
                'straight': (0.0, -4.5)
            },
            'E': {
                'left': (4.5, 1.0),
                'straight': (4.5, 0.0)
            },
            'W': {
                'left': (-4.5, -1.0),
                'straight': (-4.5, 0.0)
            }
        }