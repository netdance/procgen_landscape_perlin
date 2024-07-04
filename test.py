import numpy as np
import matplotlib.pyplot as plt

# Define the size of the grid
grid_size = 100
center = (grid_size // 2, grid_size // 2)

# Generate 1D arrays using linspace
x = np.linspace(-center[0], center[0], grid_size)
y = np.linspace(-center[1], center[1], grid_size)

# Create a 2D grid using meshgrid
X, Y = np.meshgrid(x, y)

# Compute the distance from the center
R = np.sqrt(X**2 + Y**2)

# Define the gradient function with a plateau and sharp falloff
def gradient_function(r, r_plateau, r_falloff):
    return np.piecewise(r,
                        [r <= r_plateau, 
                         (r > r_plateau) & (r <= r_plateau + r_falloff), 
                         r > r_plateau + r_falloff],
                        [1,
                         lambda r: 0.5 * (1 + np.cos(np.pi * (r - r_plateau) / r_falloff)),
                         0])

# Parameters for the plateau and falloff
r_plateau = 4  # Radius of the plateau region
r_falloff = 100  # Distance over which the falloff occurs

# Apply the gradient function
Z = gradient_function(R, r_plateau, r_falloff)

# Plotting the gradient
plt.figure(figsize=(8, 8))
plt.imshow(Z, extent=(-center[0], center[0], -center[1], center[1]), origin='lower', cmap='viridis')
plt.colorbar(label='Gradient Value')
plt.title('Radial Gradient with Plateau and Sharp Falloff')
plt.xlabel('X')
plt.ylabel('Y')
plt.show()