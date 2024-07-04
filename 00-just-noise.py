import pygame
import noise
import numpy as np

# Initialize Pygame
pygame.init()

# Screen dimensions
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Perlin Noise Animation")

# Noise parameters
scale = 100.0
octaves = 1
persistence = 0.5
lacunarity = 2.0
time_base = 0

# Colors
def noise_to_color(value):
    value = (value + 1) / 2 * 255  # Normalize to range [0, 255]
    return (int(value), int(value), int(value))

# Main loop
running = True
simplex = False
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False 
            if event.key == pygame.K_s:
                simplex = True
            if event.key == pygame.K_p:
                simplex = False
                
    # Update noise time base for animation effect
    time_base += 0.035

    # Generate and draw Perlin noise
    for y in range(height):
        for x in range(width):
            if simplex:
                noise_value = noise.snoise3(x / scale, 
                                            y / scale, 
                                            time_base, 
                                            octaves=octaves, 
                                            persistence=persistence, 
                                            lacunarity=lacunarity)
            else:
                noise_value = noise.pnoise3(x / scale, 
                                            y / scale, 
                                            time_base, 
                                            octaves=octaves, 
                                            persistence=persistence, 
                                            lacunarity=lacunarity, 
                                            repeatx=1024, 
                                            repeaty=1024, 
                                            base=42)
            color = noise_to_color(noise_value)
            screen.set_at((x, y), color)

    # Update the display
    pygame.display.flip()
    clock.tick(100)  # Limit to 100 FPS

# Quit Pygame
pygame.quit()