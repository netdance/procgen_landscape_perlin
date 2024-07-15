from typing import Tuple
import noise
import numpy as np
import pygame
from colors import BLACK, BLUE, BROWN, GREEN, SAND, WHITE

WIDTH, HEIGHT = 800, 600

def init():
    pygame.init()
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("2D Noise Terrain")
    return window

def generate_noise(width, height, scale, octaves, seed):
    noise_map = np.zeros((width, height))  # Note (width, height)
    for x in range(width):
        for y in range(height):
            noise_value = noise.snoise2(
                x / scale, y / scale, octaves=octaves, base=seed
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
    plateau_radius = 0.2
    falloff_radius = 0.7
    gradient = np.piecewise(R,
                        [R <= plateau_radius,
                         (R > plateau_radius) & (R <= falloff_radius),
                         R > falloff_radius],
                        [1,
                         lambda R: 0.5 * (1 + np.cos(np.pi * (R - plateau_radius) / (falloff_radius - plateau_radius))),
                         0])
    return gradient

def add_noise(width, height, gradient, noise_scale, noise_seed):
    noise_map = generate_noise(width, height, noise_scale, 4, noise_seed)
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

def create_map(width, height):
    # Parameters for Perlin noise
    scale = 200.0         # Larger scale for more contiguous areas
    octaves = 4          # Fewer octaves for less detail
    seed = np.random.randint(0, 100)
    # Generate noise map
    noise_map = generate_noise(width, height, scale, octaves, seed)
    # Generate radial gradient
    gradient = generate_radial_gradient(width, height)
    # Add noise, make a combined gradient
    noise_scale = 150.0
    combined_gradient = add_noise(width, height, gradient, noise_scale, seed)
    # Multiply the noise map by the combined gradient
    combined_map = noise_map * combined_gradient
    # Create terrain map
    threshold = 0.2 # Adjust this value to control the land-water ratio
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
                if event.key == pygame.K_q:
                    running = False
                if event.key == pygame.K_r:
                    surface = create_map(WIDTH, HEIGHT)

        window.blit(surface, (0, 0))
        pygame.display.flip()

if __name__ == "__main__":
    main()