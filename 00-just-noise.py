import pygame
import noise
from colors import BLACK

# Initialize Pygame
pygame.init()

# Screen dimensions
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Noise Animation")

# Font settings
font = pygame.font.SysFont('Arial', 24)

# Noise parameters
scale = 100.0
octaves = 1
altitude = 0

# Colors
def noise_to_color(value):
    value = (value + 1) / 2 * 255  # Normalize to range [0, 255]
    return (int(value), int(value), int(value))

# Main loop
running = True
noise_type = "perlin"  # Default noise type
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
            if event.key == pygame.K_s:
                noise_type = "simplex"
            if event.key == pygame.K_p:
                noise_type = "perlin"
            if event.key == pygame.K_COMMA:
                octaves = max(1, octaves - 1)
            if event.key == pygame.K_PERIOD:
                octaves += 1
            if event.key == pygame.K_LEFTBRACKET:
                scale = max(1, scale / 1.2)
            if event.key == pygame.K_RIGHTBRACKET:
                scale *= 1.2

    # Update noise altitude for animation effect
    altitude += 0.03

    # Generate and draw noise
    for y in range(height):
        for x in range(width):
            if noise_type == "simplex":
                noise_value = noise.snoise3(
                    x / scale, y / scale, altitude, octaves=octaves
                )
            else:  # Perlin
                noise_value = noise.pnoise3(
                    x / scale, y / scale, altitude, octaves=octaves
                )
            color = noise_to_color(noise_value)
            screen.set_at((x, y), color)

    # Render text
    type_text = font.render(f"Type: {noise_type}", True, BLACK)
    scale_text = font.render(f"Scale: {scale:.2f}", True, BLACK)
    octaves_text = font.render(f"Octaves: {octaves}", True, BLACK)
    altitude_text = font.render(f"Altitude: {altitude:.2f}", True, BLACK)

    # Draw text on the screen
    screen.blit(type_text, (10, 10))
    screen.blit(scale_text, (10, 40))
    screen.blit(octaves_text, (10, 70))
    screen.blit(altitude_text, (10, 100))

    # Update the display
    pygame.display.flip()