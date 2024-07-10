import random
import noise
import numpy as np
import matplotlib.pyplot as plt

def find_next_cell(alt_map, x, y):
    min_alt = alt_map[x, y]
    next_cell = (x, y)
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < alt_map.shape[0] and 0 <= ny < alt_map.shape[1] and alt_map[nx, ny] < min_alt:
            min_alt = alt_map[nx, ny]
            next_cell = (nx, ny)
    return next_cell

def create_lake(alt_map, lake_map, x, y, initial_level, max_depth):
    queue = [(x, y)]
    lake_map[x, y] = True
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    while queue:
        cx, cy = queue.pop(0)
        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            if (0 <= nx < alt_map.shape[0] and 0 <= ny < alt_map.shape[1] and
                not lake_map[nx, ny] and alt_map[nx, ny] <= initial_level and
                initial_level - alt_map[nx, ny] <= max_depth):
                lake_map[nx, ny] = True
                queue.append((nx, ny))
    
    return lake_map

def create_river(alt_map, start_x, start_y, max_lake_depth=10):
    river_map = np.zeros_like(alt_map, dtype=bool)
    lake_map = np.zeros_like(alt_map, dtype=bool)
    x, y = start_x, start_y
    
    while True:
        river_map[x, y] = True
        next_x, next_y = find_next_cell(alt_map, x, y)
        if (next_x, next_y) == (x, y):
            initial_level = alt_map[x, y]
            lake_map = create_lake(alt_map, lake_map, x, y, initial_level, max_lake_depth)
            # Find the next lowest cell outside the lake to continue the river
            new_x, new_y = np.unravel_index(np.argmin(alt_map * ~lake_map), alt_map.shape)
            if alt_map[new_x, new_y] >= alt_map[x, y]:
                break  # No lower cell found, break the loop
            x, y = new_x, new_y
        else:
            x, y = next_x, next_y
    
    return np.logical_or(river_map, lake_map)

def add_rivers(alt_map, num_rivers=5):
    river_map = np.zeros_like(alt_map, dtype=bool)
    max_altitude = alt_map.max()
    min_altitude = alt_map.min()
    threshold_min = min_altitude + (max_altitude - min_altitude) * 0.90
    threshold_max = max_altitude

    # Use logical operators to create a mask
    mask = (alt_map >= threshold_min) & (alt_map <= threshold_max)
    coordinates = np.where(mask)

    # Combine the row and column indices into a list of tuples
    coordinates_list = list(zip(coordinates[0], coordinates[1]))
    if len(coordinates_list) < num_rivers:
        num_rivers = len(coordinates_list)

    for _ in range(num_rivers):
        start_x, start_y = random.choice(coordinates_list)
        coordinates_list.remove((start_x, start_y))
        single_river_map = create_river(alt_map, start_x, start_y)
        river_map = np.logical_or(river_map, single_river_map)
    return river_map

# Example altitude map
size = 100
alt_map = np.zeros((size, size))  
for x in range(size):
    for y in range(size):
        noise_value = noise.snoise2(
            x / 50,
            y / 50,
            octaves=1,
            persistence=.5,
            lacunarity=2,
            repeatx=1024,
            repeaty=1024,
            base=4
        )
        # Normalize noise_value from [-1, 1] to [0, 1]
        alt_map[x][y] = (noise_value + 1) / 2  
    
print(alt_map)

rivers = add_rivers(alt_map, num_rivers=1)

# Visualization using matplotlib (optional)
plt.imshow(alt_map, cmap='terrain')
plt.imshow(rivers, cmap='Blues', alpha=0.5)
plt.show()