import cProfile
import logging
import pstats
import sys
from typing import Tuple
import random

import noise
import numpy as np
import pygame

# Basic configuration for logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Creating a logger
logger = logging.getLogger(__name__)

WIDTH, HEIGHT = 800, 600

PROFILE = False

def init():
    # Initialize Pygame
    pygame.init()
    # Set up display
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("2D Perlin Noise Terrain")
    return window

def generate_noise(width, height, scale, octaves, persistence, lacunarity, seed):
    noise_map = np.zeros((width, height))  
    for x in range(width):
        for y in range(height):
            noise_value = noise.snoise2(
                x / scale,
                y / scale,
                octaves=octaves,
                persistence=persistence,
                lacunarity=lacunarity,
                repeatx=1024,
                repeaty=1024,
                base=seed
            )
            # Normalize noise_value from [-1, 1] to [0, 1]
            noise_map[x][y] = (noise_value + 1) / 2  
    return noise_map

def generate_radial_gradient(width, height):
    # Create 1D arrays using linspace
    x = np.linspace(-1, 1, width)
    y = np.linspace(-1, 1, height)
    
    # Create 2D grid using meshgrid
    X, Y = np.meshgrid(x, y, indexing='ij')  # Ensure correct shape with indexing='ij'
    
    # Compute the normalized distance from the center
    R = np.sqrt(X**2 + Y**2)
    
    # Normalize distances so that the maximum distance is 1
    R = R / np.max(R)
    
    # Define the gradient function with a plateau and sharp falloff
    plateau_radius = 0.1
    falloff_radius = 1.0
    gradient = gradient_function(R, plateau_radius, falloff_radius)
    
    return gradient

def gradient_function(r, plateau_radius=0.3, falloff_radius=0.7):
    return np.piecewise(r,
                        [r <= plateau_radius,
                         (r > plateau_radius) & (r <= falloff_radius),
                         r > falloff_radius],
                        [1,
                         lambda r: 0.5 * (1 + np.cos(np.pi * (r - plateau_radius) / (falloff_radius - plateau_radius))),
                         0])

def generate_combined_gradient(width, height, gradient, noise_scale, noise_seed):
    noise_map = generate_noise(width, height, noise_scale, 4, 0.5, 2.0, noise_seed)
    combined_gradient = gradient * noise_map
    # Normalize the combined gradient
    combined_gradient = (combined_gradient - combined_gradient.min()) / (combined_gradient.max() - combined_gradient.min())
    return combined_gradient

def shade_color(color: Tuple[int, int, int], min: float, max: float, value: float) -> Tuple[int, int, int]:
    if max == 0:
        return color
    if value < 0:
        return (0,0,0)
    multiplier = float(1 - (((max - value) / max) * .75))
    bright = tuple(int(element * multiplier) for element in color)
    return bright

def get_color(value, threshold=0.15):
    # Define colors
    BLACK = (0, 0, 0)
    GREEN = (34, 139, 34)
    SAND = (231,196,150)
    BROWN = (139,69,19)
    BLUE = (0, 0, 255)
    WHITE = (255, 255, 255)
    bottom = 0
    sea = threshold 
    beach = threshold + 0.05
    grass = threshold + 0.18
    hills = threshold + 0.28
    snow = 1

    if value < sea:
        return shade_color(BLUE, bottom, sea, value)  # Deep Water
    elif value < beach:
        return shade_color(SAND, sea, beach, value)  # Beach
    elif value < grass:
        return shade_color(GREEN, beach, grass, value)  # Grass
    elif value < hills:
        return shade_color(BROWN, grass, hills, value) # Hills
    else:
        return shade_color(WHITE, hills, snow, value)  # Snow caps

def find_next_cell(alt_map, x, y):
    min_alt = alt_map[x, y]
    next_cell = (x, y)
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < alt_map.shape[0] and 0 <= ny < alt_map.shape[1] and alt_map[nx, ny] < min_alt:
            min_alt = alt_map[nx, ny]
            next_cell = (nx, ny)
    return next_cell

def create_river(alt_map, start_x, start_y):
    river_map = np.zeros_like(alt_map, dtype=bool)
    x, y = start_x, start_y
    while True:
        river_map[x, y] = True
        next_x, next_y = find_next_cell(alt_map, x, y)
        if (next_x, next_y) == (x, y):
            break;
        x, y = next_x, next_y
    return river_map

def add_rivers(alt_map, num_rivers=5):
    river_map = np.zeros_like(alt_map, dtype=bool)
    max_altitude = alt_map.max()
    threshold = max_altitude * 0.90
    coordinates = np.where(alt_map >= threshold)
    # Combine the row and column indices into a list of tuples
    coordinates_list = list(zip(coordinates[0], coordinates[1]))
    if len(coordinates_list) < num_rivers:
        num_rivers = len(coordinates_list)

    for _ in range(num_rivers):
        start_x, start_y = random.choice(coordinates_list)
        coordinates_list.remove((start_x, start_y))
        single_river_map = create_river(alt_map, start_x, start_y)
        river_map = np.logical_or(river_map, single_river_map)
    return river_map

def create_map(width, height):
    # Parameters for Perlin noise
    scale = 200.0         # Larger scale for more contiguous areas
    octaves = 4          # Fewer octaves for less detail
    persistence = 0.5     # Adjust persistence
    lacunarity = 1.9      # Adjust lacunarity
    seed = np.random.randint(0, 100)

    # Generate noise map
    noise_map = generate_noise(width, height, scale, octaves, persistence, lacunarity, seed)

    # Generate radial gradient
    gradient = generate_radial_gradient(width, height)

    # Generate combined gradient
    noise_scale = 50.0
    noise_seed = np.random.randint(0, 100)
    combined_gradient = generate_combined_gradient(width, height, gradient, noise_scale, noise_seed)

    # Multiply the noise map by the combined gradient
    combined_map = noise_map * combined_gradient

    # Add rivers to the map
    river_map = add_rivers(combined_map)

    # Create terrain map
    threshold = 0.2 # Adjust this value to control the land-water ratio
    terrain_map = np.zeros((width, height, 3), dtype=np.uint8)  
    for x in range(width):
        for y in range(height):
            if river_map[x][y]:
                color = (0, 0, 255)  # Blue color for rivers
            else:
                color = get_color(combined_map[x][y], threshold)
            terrain_map[x][y] = color  

    # Convert terrain map to Pygame surface
    surface = pygame.surfarray.make_surface(terrain_map)
    return surface

def main():
    window = init()
    surface = create_map(WIDTH, HEIGHT)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN: 
                logger.debug("keydown")
                if event.key == pygame.K_q:
                    logger.debug("keydown q")
                    running = False
                if event.key == pygame.K_r:
                    logger.debug("keydown r")
                    surface = create_map(WIDTH, HEIGHT)

        window.blit(surface, (0, 0))
        pygame.display.flip()

    if not PROFILE:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":

    if PROFILE:
        profiler = cProfile.Profile()
        profiler.enable()
        main()
        profiler.disable()

        stats = pstats.Stats(profiler)
        stats.strip_dirs()
        stats.sort_stats('cumulative')
        stats.print_stats()
    else:
        main()