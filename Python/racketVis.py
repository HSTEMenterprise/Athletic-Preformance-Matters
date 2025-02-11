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
# Open image and resize to 100x100 (no downsampling below that)
image = Image.open(filename).resize((100, 100))
# Extract RGB and normalize to [0,1]
img = np.array(image)[:, :, :3] / 255.0  
# Add alpha channel if necessary so that img becomes (M, N, 4)
if img.shape[2] == 3:
    alpha_channel = np.ones((img.shape[0], img.shape[1], 1))
    img = np.concatenate((img, alpha_channel), axis=-1)
# Set background (black) to transparent (adjust threshold as needed)
bg_mask = np.all(img[..., :3] < 0.05, axis=-1)
img[bg_mask, 3] = 0
image_array = img  # shape: (M, N, 4)

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
z = np.zeros_like(x)  # Flat surface

# --- Vectorized facet computation ---
def compute_facets(xgrid, ygrid, zgrid):
    """
    Compute facets for a grid given by xgrid, ygrid, zgrid (each of shape (M,N)).
    Returns an array of shape ((M-1)*(N-1), 4, 3) where each facet (quadrilateral) has 4 vertices.
    """
    v1 = np.stack([xgrid[:-1, :-1], ygrid[:-1, :-1], zgrid[:-1, :-1]], axis=-1)
    v2 = np.stack([xgrid[:-1, 1:],   ygrid[:-1, 1:],   zgrid[:-1, 1:]], axis=-1)
    v3 = np.stack([xgrid[1:, 1:],    ygrid[1:, 1:],    zgrid[1:, 1:]], axis=-1)
    v4 = np.stack([xgrid[1:, :-1],   ygrid[1:, :-1],   zgrid[1:, :-1]], axis=-1)
    facets = np.stack([v1, v2, v3, v4], axis=2)  # shape: (M-1, N-1, 4, 3)
    return facets.reshape(-1, 4, 3)

# --- Vectorized facet color computation ---
def compute_facet_colors(image_arr):
    """
    Compute facecolor for each cell by averaging the colors of the corresponding 2x2 block.
    Returns an array of shape ((M-1)*(N-1), 4) (RGBA per facet).
    """
    colors = (image_arr[:-1, :-1, :] +
              image_arr[:-1, 1:, :] +
              image_arr[1:, :-1, :] +
              image_arr[1:, 1:, :]) / 4.0
    return colors.reshape(-1, 4)

# Precompute the facet colors from the original image (they remain constant)
facet_colors_static = compute_facet_colors(image_array)

# --- Plot the initial surface ---
# Initially, compute facets from the unrotated grid.
initial_facets = compute_facets(x, y, z)
# Create a surface; note that we pass the initial facecolors reshaped to (M-1, N-1, 4)
image_surface = ax.plot_surface(x, y, z, rstride=1, cstride=1,
                                facecolors=facet_colors_static.reshape(M-1, N-1, 4),
                                shade=False, linewidth=0, antialiased=False, edgecolor='none')

# Fix the axes (and keep the camera fixed)
ax.set_xlim(-10, 10)
ax.set_ylim(-10, 10)
ax.set_zlim(-10, 10)
ax.set_xlabel("X-axis")
ax.set_ylabel("Y-axis")
ax.set_zlabel("Z-axis")
# Optionally hide the axes if you want just the object:
# ax.set_axis_off()

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
    # Get current rotation angles (pitch, roll, yaw)
    pitch, roll, yaw = data[frame]
    R = rotation_matrix(pitch, roll, yaw)
    
    # Apply rotation to the grid coordinates (vectorized)
    coords = np.vstack([x.ravel(), y.ravel(), z.ravel()])  # shape: (3, M*N)
    rotated = R @ coords
    x_rot = rotated[0].reshape(x.shape)
    y_rot = rotated[1].reshape(y.shape)
    z_rot = rotated[2].reshape(z.shape)
    
    # Recompute facets for the rotated grid (vectorized)
    new_facets = compute_facets(x_rot, y_rot, z_rot)
    
    # Update the Poly3DCollection vertices.
    image_surface.set_verts(new_facets.tolist())
    
    # Update facecolors using the precomputed static facet colors
    image_surface.set_facecolors(facet_colors_static)
    
    # Do not update the camera view so that it stays fixed.
    return image_surface,

# --- Create the animation ---
ani = animation.FuncAnimation(fig, update, frames=len(data), interval=100, blit=False)

plt.show()
