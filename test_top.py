import random

import noise
import numpy as np

# Example 2D array of floats
array_2d = np.array([
    [0.1, 0.8, 0.9],
    [0.7, 0.85, 0.3],
    [0.6, 0.4, 0.95]
])

size = 25
array_2d = np.zeros((size, size))  
for x in range(size):
    for y in range(size):
        noise_value = noise.snoise2(
            x / 200,
            y / 200,
            octaves=4,
            persistence=1,
            lacunarity=1,
            repeatx=1024,
            repeaty=1024,
            base=35
        )
        # Normalize noise_value from [-1, 1] to [0, 1]
        array_2d[x][y] = (noise_value + 1) / 2  

# Find the maximum value in the array
max_value = np.max(array_2d)

# Calculate the threshold for values within 5% of the maximum value
threshold = max_value * 0.95

# Get the coordinates of all elements within 10% of the maximum value
coordinates = np.where(array_2d >= threshold)

# Combine the row and column indices into a list of tuples
coordinates_list = list(zip(coordinates[0], coordinates[1]))

chosen_coord = random.choice(coordinates_list)

print(f"Maximum value: {max_value}")
print(f"Threshold value: {threshold}")
print(f"Number of coordinates within threshhold: {len(coordinates_list)}")
print(f"Chosen Coordinate: {chosen_coord}")