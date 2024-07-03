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
    noise_map = np.zeros((width, height))  # Note (width, height)
    for x in range(width):
        for y in range(height):
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
            # Normalize noise_value from [-1, 1] to [0, 1]
            noise_map[x][y] = (noise_value + 1) / 2  # Note (x, y) indexing
    return noise_map

def generate_radial_gradient(width, height):
    center_x, center_y = width // 2, height // 2
    max_distance = np.sqrt(center_x**2 + center_y**2)
    gradient = np.zeros((width, height))  # Note (width, height)
    for x in range(width):
        for y in range(height):
            distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
            gradient[x][y] = distance / max_distance  # Note (x, y) indexing
            logger.debug("x %s y %s gradient %s", x, y, gradient[x][y])
    # Invert the gradient
    gradient = 1 - gradient
    # Apply a power function to make the falloff steeper
    gradient = gradient**3
    return gradient

def generate_combined_gradient(width, height, gradient, noise_scale, noise_seed):
    noise_map = generate_perlin_noise(width, height, noise_scale, 4, 0.5, 2.0, noise_seed)
    combined_gradient = gradient * noise_map
    # Normalize the combined gradient
    combined_gradient = (combined_gradient - combined_gradient.min()) / (combined_gradient.max() - combined_gradient.min())
    return combined_gradient

def get_color(value, threshold=0.15):
    # Define colors
    BLACK = (0, 0, 0)
    GREEN = (34, 139, 34)
    SAND = (231,196,150)
    BROWN = (139,69,19)
    BLUE = (0, 0, 255)
    WHITE = (255, 255, 255)
    if value < threshold - 0.05:
        return BLUE  # Deep Water
    elif value < threshold:
        return SAND  # Beach
    elif value < threshold + 0.22:
        return GREEN  # Grass
    elif value < threshold + 0.30:
        return BROWN # Hills
    else:
        return WHITE  # Snow caps

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

    # Generate combined gradient
    noise_scale = 50.0
    noise_seed = np.random.randint(0, 100)
    combined_gradient = generate_combined_gradient(width, height, gradient, noise_scale, noise_seed)

    # Multiply the noise map by the combined gradient
    combined_map = noise_map * combined_gradient

    # Create terrain map
    threshold = 0.15  # Adjust this value to control the land-water ratio
    terrain_map = np.zeros((width, height, 3), dtype=np.uint8)  
    for x in range(width):
        for y in range(height):
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