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

def generate_noise(width, height, scale, octaves, persistence, lacunarity, seed):
    noise_map = np.zeros((width, height))  # Note (width, height)
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
            noise_map[x][y] = (noise_value + 1) / 2  # Note (x, y) indexing
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
    falloff_radius = 0.9
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

    # Create terrain map
    threshold = 0.2  # Adjust this value to control the land-water ratio
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