import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, Any

def create_layout_visualization(
    length: float,
    width: float,
    layout_data: Dict[str, Any],
    room_type: str
) -> plt.Figure:
    """
    Create a 2D visualization of the room layout.
    
    Args:
        length (float): Room length
        width (float): Room width
        layout_data (Dict[str, Any]): Layout suggestions data
        room_type (str): Type of room
    
    Returns:
        plt.Figure: Matplotlib figure with the visualization
    """
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Draw room boundaries
    room = plt.Rectangle((0, 0), length, width, fill=False, color='black')
    ax.add_patch(room)
    
    # Color scheme for different furniture types
    colors = {
        'sofa': '#FF9999',
        'coffee_table': '#66B2FF',
        'tv_stand': '#99FF99',
        'armchair': '#FFCC99',
        'bed': '#FF99CC',
        'wardrobe': '#99CCFF',
        'desk': '#FFB366',
        'dining_table': '#99FFCC',
        'counter': '#FF99FF',
        'storage': '#FFFF99'
    }
    
    # Plot furniture
    if 'layout_options' in layout_data and layout_data['layout_options']:
        layout = layout_data['layout_options'][0]  # Use first layout option
        
        # Position furniture with simple layout algorithm
        furniture_layout = position_furniture(layout['furniture'], length, width)
        
        # Draw furniture
        for item in furniture_layout:
            color = colors.get(item['type'], '#CCCCCC')
            furniture = plt.Rectangle(
                item['position'],
                item['dimensions']['length'],
                item['dimensions']['width'],
                fill=True,
                color=color,
                alpha=0.7
            )
            ax.add_patch(furniture)
            
            # Add label
            center_x = item['position'][0] + item['dimensions']['length']/2
            center_y = item['position'][1] + item['dimensions']['width']/2
            ax.text(center_x, center_y, item['type'].replace('_', ' ').title(),
                   ha='center', va='center', fontsize=8)
    
    # Set axis properties
    ax.set_xlim(-0.5, length + 0.5)
    ax.set_ylim(-0.5, width + 0.5)
    ax.set_aspect('equal')
    ax.grid(True, linestyle='--', alpha=0.6)
    
    # Add title and labels
    ax.set_title(f"{room_type} Layout Visualization")
    ax.set_xlabel("Length (meters)")
    ax.set_ylabel("Width (meters)")
    
    # Add legend
    legend_elements = [plt.Rectangle((0, 0), 1, 1, fc=color, alpha=0.7)
                      for color in colors.values()]
    ax.legend(legend_elements, [k.replace('_', ' ').title() 
                              for k in colors.keys()],
             loc='center left', bbox_to_anchor=(1, 0.5))
    
    plt.tight_layout()
    return fig

def position_furniture(
    furniture: list,
    room_length: float,
    room_width: float
) -> list:
    """
    Position furniture items in the room.
    
    Args:
        furniture (list): List of furniture items
        room_length (float): Room length
        room_width (float): Room width
    
    Returns:
        list: Furniture items with positions
    """
    positioned_furniture = []
    grid_size = 0.5  # Grid size for furniture placement
    
    # Create occupancy grid
    grid_length = int(room_length / grid_size)
    grid_width = int(room_width / grid_size)
    occupancy_grid = np.zeros((grid_width, grid_length))
    
    # Sort furniture by area (largest first)
    sorted_furniture = sorted(
        furniture,
        key=lambda x: x['dimensions']['length'] * x['dimensions']['width'],
        reverse=True
    )
    
    for item in sorted_furniture:
        # Convert furniture dimensions to grid units
        item_length = int(item['dimensions']['length'] / grid_size)
        item_width = int(item['dimensions']['width'] / grid_size)
        
        # Find suitable position
        position = find_furniture_position(
            occupancy_grid,
            item_length,
            item_width,
            grid_size
        )
        
        if position:
            # Update occupancy grid
            x, y = position
            occupancy_grid[y:y+item_width, x:x+item_length] = 1
            
            # Add positioned furniture
            positioned_item = item.copy()
            positioned_item['position'] = (x * grid_size, y * grid_size)
            positioned_furniture.append(positioned_item)
    
    return positioned_furniture

def find_furniture_position(
    occupancy_grid: np.ndarray,
    item_length: int,
    item_width: int,
    grid_size: float
) -> tuple:
    """
    Find a suitable position for furniture item.
    
    Args:
        occupancy_grid (np.ndarray): Room occupancy grid
        item_length (int): Furniture length in grid units
        item_width (int): Furniture width in grid units
        grid_size (float): Size of grid cells
    
    Returns:
        tuple: (x, y) position or None if no position found
    """
    grid_height, grid_width = occupancy_grid.shape
    
    # Try to find empty space
    for y in range(grid_height - item_width + 1):
        for x in range(grid_width - item_length + 1):
            if not np.any(occupancy_grid[y:y+item_width, x:x+item_length]):
                return (x, y)
    
    return None
