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

# Define the plateau and falloff
plateau_radius = 0.3  # The radius of the plateau
falloff_radius = 0.7  # The start of the falloff

# Define the gradient function with a plateau and sharp falloff
def gradient_function(r, plateau_radius, falloff_radius):
    return np.piecewise(r,
                        [r <= plateau_radius,
                         (r > plateau_radius) & (r <= falloff_radius),
                         r > falloff_radius],
                        [1,
                         lambda r: 0.5 * (1 + np.cos(np.pi * (r - plateau_radius) / (falloff_radius - plateau_radius))),
                         0])

# Apply the gradient function
Z = gradient_function(R, plateau_radius, falloff_radius)

# Plotting the gradient
plt.figure(figsize=(8, 8))
plt.imshow(Z, extent=(-center[0], center[0], -center[1], center[1]), origin='lower', cmap='viridis')
plt.colorbar(label='Gradient Value')
plt.title('Radial Gradient with Plateau and Sharp Falloff')
plt.xlabel('X')
plt.ylabel('Y')
plt.show()