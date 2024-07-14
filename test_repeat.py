import noise
import numpy as np
import matplotlib.pyplot as plt

# Parameters
width, height = 200, 200  # Increased size for better visualization
scale = 20.0
repeatx = 50
repeaty = 50

# Generate noise
noise_grid = np.zeros((width, height))
for i in range(width):
    for j in range(height):
        noise_grid[i][j] = noise.pnoise2(i / scale,
                                         j / scale,
                                         octaves=1,
                                         repeatx=repeatx,
                                         repeaty=repeaty,
                                         base=10)

# Display the noise
plt.imshow(noise_grid, cmap='gray')
plt.colorbar()
plt.show()