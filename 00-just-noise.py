import pygame
import noise
from opensimplex import OpenSimplex

# Initialize Pygame
pygame.init()

# Screen dimensions
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Noise Animation")

# Noise parameters
scale = 100.0
octaves = 1
persistence = 0.5
lacunarity = 2.0
altitude = 0

# OpenSimplex instance
simplex_noise = OpenSimplex(seed=42)

# Colors
def noise_to_color(value):
    value = (value + 1) / 2 * 255  # Normalize to range [0, 255]
    return (int(value), int(value), int(value))

# Main loop
running = True
noise_type = 'perlin'  # Default noise type
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False 
            if event.key == pygame.K_s:
                noise_type = 'simplex'
            if event.key == pygame.K_p:
                noise_type = 'perlin'
            if event.key == pygame.K_o:
                noise_type = 'opensimplex'
            if event.key == pygame.K_COMMA:
                octaves = max(1, octaves - 1)
            if event.key == pygame.K_PERIOD:
                octaves += 1
            if event.key == pygame.K_MINUS:
                lacunarity = max(1.5, lacunarity - 0.1)
            if event.key == pygame.K_EQUALS:
                lacunarity += 0.1
            if event.key == pygame.K_LEFTBRACKET:
                scale = max(1, scale / 1.2)
            if event.key == pygame.K_RIGHTBRACKET:
                scale *= 1.2

    # Update noise altitude for animation effect
    altitude += 0.035

    # Generate and draw noise
    for y in range(height):
        for x in range(width):
            if noise_type == 'simplex':
                noise_value = noise.snoise3(x / scale, 
                                            y / scale, 
                                            altitude, 
                                            octaves=octaves, 
                                            persistence=persistence, 
                                            lacunarity=lacunarity)
            elif noise_type == 'opensimplex':
                # Warning, dead slow, about one frame every 3 seconds on my box
                noise_value = simplex_noise.noise3(x / scale, y / scale, altitude)
            else:  # Perlin
                noise_value = noise.pnoise3(x / scale, 
                                            y / scale, 
                                            altitude, 
                                            octaves=octaves, 
                                            persistence=persistence, 
                                            lacunarity=lacunarity
                                            )
            color = noise_to_color(noise_value)
            screen.set_at((x, y), color)

    # Update the display
    pygame.display.flip()
    print(f"Scale {scale} Octaves {octaves} Lacunarity {lacunarity}")

