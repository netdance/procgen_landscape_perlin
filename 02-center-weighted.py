import noise
import numpy as np
import pygame
from colors import BLACK, GREEN, WHITE, SAND, BLUE, BROWN

WIDTH, HEIGHT = 800, 600

def init():
    # Initialize Pygame
    pygame.init()
    # Set up display
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

def get_color(value, threshold=0.15):
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
    scale = 150.0         # Larger scale for more contiguous areas
    octaves = 5           # Fewer octaves for less detail
    seed = np.random.randint(0, 100)

    # Generate noise map
    noise_map = generate_noise(width, height, scale, octaves, seed)

    # Generate radial gradient
    gradient = generate_radial_gradient(width, height)

    # Multiply the noise map by the gradient
    combined_map = noise_map * gradient

    # Create terrain map
    threshold = 0.3  # Adjust this value to control the land-water ratio
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
