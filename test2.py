import numpy as np
import matplotlib.pyplot as plt

# Define the size of the grid
grid_size = 10
center = (grid_size // 2, grid_size // 2)

# Generate 1D arrays using linspace
x = np.linspace(-center[0], center[0], grid_size)
y = np.linspace(-center[1], center[1], grid_size)

# Create a 2D grid using meshgrid
X, Y = np.meshgrid(x, y)

# Compute the distance from the center
R = np.sqrt(X**2 + Y**2)

# Normalize the distances so that the maximum distance is 1
R = R / np.max(R)

# Invert the distances to have 1 at the center and 0 at the edges
R = 1 - R

R = R ** 3

# Plotting the gradient
plt.figure(figsize=(8, 8))
plt.imshow(R, extent=(-center[0], center[0], -center[1], center[1]), origin='lower', cmap='viridis')
plt.colorbar(label='Gradient Value')
plt.title('Radial Gradient with Plateau and Sharp Falloff')
plt.xlabel('X')
plt.ylabel('Y')
plt.show()