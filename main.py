import cProfile
import logging
import pstats
import sys

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

def generate_perlin_noise(width, height, scale, octaves, persistence, lacunarity, seed):
    noise_map = np.zeros((height, width))  # Note (height, width)
    for y in range(height):
        for x in range(width):
            noise_value = noise.pnoise2(
                x / scale,
                y / scale,
                octaves=octaves,
                persistence=persistence,
                lacunarity=lacunarity,
                repeatx=1024,
                repeaty=1024,
                base=seed
            )
            noise_map[y][x] = noise_value  # Note (y, x) indexing
    return noise_map

def generate_radial_gradient(width, height):
    center_x, center_y = width // 2, height // 2
    max_distance = np.sqrt(center_x**2 + center_y**2)
    gradient = np.zeros((height, width))  # Note (height, width)
    for y in range(height):
        for x in range(width):
            distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
            gradient[y][x] = distance / max_distance  # Note (y, x) indexing
            logger.debug("x %s y %s gradient %s", x, y, gradient[y][x])
    return gradient

def get_color(value, threshold=0.15):
    # Define colors
    BLACK = (0, 0, 0)
    GREEN = (34, 139, 34)
    BROWN = (119, 69, 19)
    BLUE = (0, 0, 255)
    WHITE = (255, 255, 255)
    if value < threshold - 0.15:
        return BLUE  # Deep Water
    elif value < threshold:
        return BROWN  # Beach
    elif value < threshold + 0.25:
        return GREEN  # Grass
    else:
        return WHITE  # Snow

def create_map(width, height):
    # Parameters for Perlin noise
    scale = 200.0         # Larger scale for more contiguous areas
    octaves = 4          # Fewer octaves for less detail
    persistence = 0.75     # Adjust persistence
    lacunarity = 1.9      # Adjust lacunarity
    seed = np.random.randint(0, 100)

    # Generate noise map
    noise_map = generate_perlin_noise(width, height, scale, octaves, persistence, lacunarity, seed)

    # Generate radial gradient
    gradient = generate_radial_gradient(width, height)

    # Subtract the gradient from the noise map to lower the edges
    combined_map = noise_map - gradient

    # Create terrain map
    threshold = -0.25  # Adjust this value to control the land-water ratio
    terrain_map = np.zeros((height, width, 3), dtype=np.uint8)  
    for y in range(height):
        for x in range(width):
            color = get_color(combined_map[y][x], threshold)  
            terrain_map[y][x] = color  

    # Convert terrain map to Pygame surface
    surface = pygame.surfarray.make_surface(terrain_map.transpose((1, 0, 2)))
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