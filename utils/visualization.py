import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def setup_visualization(config):
    """Initialize the visualization components"""
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    scat = ax.scatter([], [], s=80)

    # Draw roads and lanes
    ax.add_patch(patches.Rectangle((-5, -2.0), 10, 4, color='gray', zorder=0))
    ax.add_patch(patches.Rectangle((-2.0, -5), 4, 10, color='gray', zorder=0))

    # Draw lane markers
    for d in config.directions:
        for lane in config.all_lane_types:
            x, y = config.lane_positions[d][lane]
            ax.add_patch(patches.Circle((x, y), 0.05, color='black', zorder=1))

    # Setup traffic lights
    light_positions = {
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

    light_patches = {
        d: {
            'left': ax.add_patch(patches.Rectangle(light_positions[d]['left'], 0.2, 0.2, color='red', zorder=3)),
            'straight': ax.add_patch(patches.Rectangle(light_positions[d]['straight'], 0.2, 0.2, color='red', zorder=3))
        }
        for d in config.directions
    }

    # Initialize text objects for car counts
    text_counters = {
        d: {
            'left': ax.text(light_positions[d]['left'][0] + 0.3, light_positions[d]['left'][1] - 0.1, '0', fontsize=10, ha='left', va='center'),
            'straight': ax.text(light_positions[d]['straight'][0] + 0.3, light_positions[d]['straight'][1] - 0.1, '0', fontsize=10, ha='left', va='center')
        }
        for d in config.directions
    }

    # Add direction labels
    for d in config.directions:
        ax.text(light_positions[d]['left'][0] + 0.3, light_positions[d]['left'][1] + 0.1,
                f"{d}-left", fontsize=8, ha='left', va='center')
        ax.text(light_positions[d]['straight'][0] + 0.3, light_positions[d]['straight'][1] + 0.1,
                f"{d}-straight/right", fontsize=8, ha='left', va='center')

    return fig, ax, scat, light_patches, text_counters

def update_visualization(ax, scat, light_patches, active_cars, light_state, allowed_dirs, time_step, config, queues, text_counters):
    """Update all visualization elements for each frame"""
    # Update car positions
    positions = [car.position for car in active_cars]
    colors = [car.color for car in active_cars]
    x, y = zip(*positions) if positions else ([], [])
    scat.set_offsets(np.column_stack((x, y)))
    scat.set_color(colors)

    # Update traffic lights
    light_dir, light_lane = light_state
    for d in config.directions:
        if d in allowed_dirs:
            if light_lane == 'left':
                light_patches[d]['left'].set_color('orange')
                light_patches[d]['straight'].set_color('red')
            else:
                light_patches[d]['left'].set_color('red')
                light_patches[d]['straight'].set_color('green')
        else:
            light_patches[d]['left'].set_color('red')
            light_patches[d]['straight'].set_color('red')

        # Update car counts
        text_counters[d]['left'].set_text(str(len(queues[d]['left'])))
        text_counters[d]['straight'].set_text(str(len(queues[d]['straight_forward']) + len(queues[d]['right']))) # Combine straight and right

    # Update title with current time and light state
    ax.set_title(f"Time {time_step} | Light: {light_dir}-{light_lane}")