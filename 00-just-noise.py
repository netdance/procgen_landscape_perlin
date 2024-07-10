import pyfastnoiselite.pyfastnoiselite
import pygame
import noise
import numpy as np
from opensimplex import OpenSimplex
import logging
import pyfastnoiselite

# Basic configuration for logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Creating a logger
logger = logging.getLogger(__name__)

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
time_base = 0

# OpenSimplex instance
simplex_noise = OpenSimplex(seed=42)

# Colors
def noise_to_color(value):
    value = (value + 1) / 2 * 255  # Normalize to range [0, 255]
    return (int(value), int(value), int(value))

# Main loop
running = True
noise_type = 'perlin'  # Default noise type
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False 
                logger.debug("quitting")
            if event.key == pygame.K_s:
                noise_type = 'simplex'
                logger.debug("switching to simplex")
            if event.key == pygame.K_p:
                noise_type = 'perlin'
                logger.debug("switching to perlin")
            if event.key == pygame.K_o:
                noise_type = 'opensimplex'
                logger.debug("switching to opensimplex")
                
    # Update noise time base for animation effect
    time_base += 0.035
    logger.debug("TimeBase %s", time_base)

    # Generate and draw noise
    for y in range(height):
        for x in range(width):
            if noise_type == 'simplex':
                noise_value = noise.snoise3(x / scale, 
                                            y / scale, 
                                            time_base, 
                                            octaves=octaves, 
                                            persistence=persistence, 
                                            lacunarity=lacunarity)
            elif noise_type == 'opensimplex':
                noise_value = simplex_noise.noise3(x / scale, y / scale, time_base)
            else:  # Perlin
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
    print(clock.get_fps())
    clock.tick(30)  # Limit to 30 FPS

# Quit Pygame
pygame.quit()