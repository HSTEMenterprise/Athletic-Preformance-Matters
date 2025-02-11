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

# --- Load image and prepare texture (facecolors) ---
filename = select_file()
image = Image.open(filename).resize((100, 100))  # Use 100x100 resolution
# Extract RGB and normalize to [0,1]
image_array = np.array(image)[:, :, :3] / 255.0  
# Add alpha channel if needed (making it RGBA)
if image_array.shape[2] == 3:
    alpha_channel = np.ones((image_array.shape[0], image_array.shape[1], 1))
    image_array = np.concatenate((image_array, alpha_channel), axis=-1)
# Convert nearly black background to transparent (adjust threshold as needed)
bg_mask = np.all(image_array[..., :3] < 0.05, axis=-1)
image_array[bg_mask, 3] = 0

# --- Load rotation data from CSV (pitch, roll, yaw) ---
filename2 = select_file()
data = []
with open(filename2, 'r') as file:
    reader = csv.reader(file, delimiter=' ')
    for row in reader:
        cleaned = [float(val) for val in row if val]
        data.append(cleaned)
data = np.array(data)  # shape: (num_frames, 3)

# --- Create figure and 3D axes ---
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# --- Build the initial grid ---
M, N = image_array.shape[0], image_array.shape[1]
x_lin = np.linspace(-5, 5, N)
y_lin = np.linspace(-5, 5, M)
x, y = np.meshgrid(x_lin, y_lin)
z = np.zeros_like(x)  # flat surface

# --- Vectorized facet computation ---
def compute_facets(xgrid, ygrid, zgrid):
    v1 = np.stack([xgrid[:-1, :-1], ygrid[:-1, :-1], zgrid[:-1, :-1]], axis=-1)
    v2 = np.stack([xgrid[:-1, 1:],   ygrid[:-1, 1:],   zgrid[:-1, 1:]], axis=-1)
    v3 = np.stack([xgrid[1:, 1:],    ygrid[1:, 1:],    zgrid[1:, 1:]], axis=-1)
    v4 = np.stack([xgrid[1:, :-1],   ygrid[1:, :-1],   zgrid[1:, :-1]], axis=-1)
    facets = np.stack([v1, v2, v3, v4], axis=2)  # shape: (M-1, N-1, 4, 3)
    return facets.reshape(-1, 4, 3)

# --- Vectorized facet color computation ---
def compute_facet_colors(image_arr):
    colors = (image_arr[:-1, :-1, :] +
              image_arr[:-1, 1:, :] +
              image_arr[1:, :-1, :] +
              image_arr[1:, 1:, :]) / 4.0
    return colors.reshape(-1, 4)

# Precompute facet colors (texture remains fixed)
facet_colors_static = compute_facet_colors(image_array)

# --- Plot the initial surface ---
initial_facets = compute_facets(x, y, z)
image_surface = ax.plot_surface(x, y, z, rstride=1, cstride=1,
                                facecolors=facet_colors_static.reshape(M-1, N-1, 4),
                                shade=False, linewidth=0, antialiased=False, edgecolor='none')

# Fix axes and keep camera fixed
ax.set_xlim(-10, 10)
ax.set_ylim(-10, 10)
ax.set_zlim(-10, 10)
ax.set_xlabel("X-axis")
ax.set_ylabel("Y-axis")
ax.set_zlabel("Z-axis")
# (Do not call ax.view_init here so the camera remains fixed)

# --- Rotation matrix function ---
def rotation_matrix(pitch, roll, yaw):
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
    # Get current rotation angles
    pitch, roll, yaw = data[frame]
    R = rotation_matrix(pitch, roll, yaw)
    
    # --- Pivot adjustment: rotate about the handle instead of the center ---
    # Define the pivot (handle) coordinate.
    # For example, if the handle is at the bottom center of the racket,
    # and your grid spans -5 to 5 in both x and y, you might choose:
    pivot = np.array([[0], [5], [0]])  # Adjust this as needed!
    
    # Get original grid coordinates and subtract the pivot to center on the handle.
    coords = np.vstack([x.ravel(), y.ravel(), z.ravel()])  # shape: (3, M*N)
    coords_shifted = coords - pivot  # shift so pivot is at origin
    
    # Apply rotation to the shifted coordinates.
    rotated = R @ coords_shifted
    
    # Add the pivot back to move back to the original coordinate system.
    rotated_coords = rotated + pivot
    x_rot = rotated_coords[0].reshape(x.shape)
    y_rot = rotated_coords[1].reshape(y.shape)
    z_rot = rotated_coords[2].reshape(z.shape)
    
    # Recompute facets from the rotated grid (vectorized)
    new_facets = compute_facets(x_rot, y_rot, z_rot)
    
    # Update the Poly3DCollection vertices and facecolors.
    image_surface.set_verts(new_facets.tolist())
    image_surface.set_facecolors(facet_colors_static)
    
    return image_surface,

# --- Create the animation ---
ani = animation.FuncAnimation(fig, update, frames=len(data), interval=100, blit=False)

plt.show()
