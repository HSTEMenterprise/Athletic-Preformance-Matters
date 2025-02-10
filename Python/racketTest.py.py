import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
from PIL import Image
import csv

# --- Utility to select file ---
def select_file():
    from tkinter import filedialog
    return filedialog.askopenfilename(title="Select a file", filetypes=[("all files", "*.*")])

# --- Load image and prepare facecolors ---
filename = select_file()
image = Image.open(filename)  # Downscale for performance
# Extract RGB channels and normalize to [0,1]
image_array = np.array(image)[:, :, :3] / 255.0  
# Add alpha channel if needed so image_array becomes (M, N, 4)
if image_array.shape[2] == 3:
    alpha_channel = np.ones((image_array.shape[0], image_array.shape[1], 1))
    image_array = np.concatenate((image_array, alpha_channel), axis=-1)

# --- Load rotation data from CSV (pitch, roll, yaw) ---
filename2 = select_file()
data = []
with open(filename2, 'r') as file:
    reader = csv.reader(file, delimiter=' ')
    for row in reader:
        cleaned_row = [float(value) for value in row if value]
        data.append(cleaned_row)
data = np.array(data)

# --- Create figure and 3D axes ---
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# --- Create initial grid ---
M, N = image_array.shape[0], image_array.shape[1]
x = np.linspace(-5, 5, N)
y = np.linspace(-5, 5, M)
x, y = np.meshgrid(x, y)
z = np.zeros_like(x)  # flat surface

# --- Plot the initial surface ---
# We use the initial grid to create facets.
def compute_facets(xgrid, ygrid, zgrid):
    facets = []
    for i in range(xgrid.shape[0] - 1):
        for j in range(xgrid.shape[1] - 1):
            # Each facet is a quadrilateral with 4 vertices:
            facet = np.array([
                [xgrid[i, j],     ygrid[i, j],     zgrid[i, j]],
                [xgrid[i, j+1],   ygrid[i, j+1],   zgrid[i, j+1]],
                [xgrid[i+1, j+1], ygrid[i+1, j+1], zgrid[i+1, j+1]],
                [xgrid[i+1, j],   ygrid[i+1, j],   zgrid[i+1, j]]
            ])
            facets.append(facet)
    return facets

# Compute initial facets and facecolors
initial_facets = compute_facets(x, y, z)

def compute_facet_colors(xgrid, ygrid, zgrid, image_arr):
    # For each facet (cell), compute the average of the four corner colors.
    facet_colors = []
    for i in range(image_arr.shape[0]-1):
        for j in range(image_arr.shape[1]-1):
            cell = image_arr[i:i+2, j:j+2, :]  # shape (2,2,4)
            color = cell.mean(axis=(0,1))       # average RGBA
            facet_colors.append(color)
    return np.array(facet_colors)

initial_facet_colors = compute_facet_colors(x, y, z, image_array)

# Plot the surface using the initial facets and colors.
image_surface = ax.plot_surface(x, y, z, rstride=1, cstride=1,
                                facecolors=image_array, shade=False)
# Note: We'll update the vertices of the underlying Poly3DCollection.

# Set axis limits and labels
ax.set_xlim(-10, 10)
ax.set_ylim(-10, 10)
ax.set_zlim(-10, 10)
ax.set_xlabel("X-axis")
ax.set_ylabel("Y-axis")
ax.set_zlabel("Z-axis")

# --- Rotation matrix function ---
def rotation_matrix(pitch, roll, yaw):
    # Convert angles (in degrees) to radians.
    pitch, roll, yaw = np.radians([pitch, roll, yaw])
    Rx = np.array([[1, 0, 0],
                   [0, np.cos(pitch), -np.sin(pitch)],
                   [0, np.sin(pitch), np.cos(pitch)]])
    Ry = np.array([[np.cos(roll), 0, np.sin(roll)],
                   [0, 1, 0],
                   [-np.sin(roll), 0, np.cos(roll)]])
    Rz = np.array([[np.cos(yaw), -np.sin(yaw), 0],
                   [np.sin(yaw), np.cos(yaw), 0],
                   [0, 0, 1]])
    return Rz @ Ry @ Rx

# --- Animation update function ---
def update(frame):
    # Get current pitch, roll, yaw from data
    pitch, roll, yaw = data[frame]
    R = rotation_matrix(pitch, roll, yaw)
    
    # Apply rotation to the entire grid.
    # Stack coordinates for vectorized transformation.
    coords = np.vstack([x.ravel(), y.ravel(), z.ravel()])  # shape (3, M*N)
    rotated = R @ coords
    x_rot = rotated[0, :].reshape(x.shape)
    y_rot = rotated[1, :].reshape(y.shape)
    z_rot = rotated[2, :].reshape(z.shape)
    
    # Recompute facets from rotated grid.
    new_facets = compute_facets(x_rot, y_rot, z_rot)
    new_facet_colors = compute_facet_colors(x_rot, y_rot, z_rot, image_array)
    
    # Update the Poly3DCollection vertices and facecolors.
    image_surface.set_verts(new_facets)
    image_surface.set_facecolors(new_facet_colors)
    
    # Optionally, adjust the view so the surface remains visible.
    #ax.view_init(elev=20, azim=frame % 360)
    return image_surface,

# --- Create the animation ---
ani = animation.FuncAnimation(fig, update, frames=len(data), interval=100, blit=False)

plt.show()
