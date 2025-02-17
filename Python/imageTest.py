import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
from PIL import Image

# Load the image
image_path = "../Assets/racket.png"  # Replace with your image path
img = np.array(Image.open(image_path)) / 255.0  # Normalize image data to [0, 1]

# Create a figure and 3D axis
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Function to create a rotated and translated image plane
def transform_image(img, translation, rotation):
    """
    Applies translation and rotation to the image plane.

    Parameters:
    - img: The 2D image array.
    - translation: (tx, ty, tz), the translation vector.
    - rotation: (rx, ry, rz), the rotation angles (in degrees) around X, Y, Z axes.

    Returns:
    - x, y, z: Transformed coordinates of the image plane.
    - img: Original image data.
    """
    h, w, _ = img.shape
    x, y = np.meshgrid(np.linspace(-1, 1, w), np.linspace(-1, 1, h))
    z = np.zeros_like(x)

    # Flatten the image coordinates
    coords = np.vstack((x.ravel(), y.ravel(), z.ravel()))

    # Rotation matrices
    rx, ry, rz = np.radians(rotation)
    Rx = np.array([[1, 0, 0],
                   [0, np.cos(rx), -np.sin(rx)],
                   [0, np.sin(rx), np.cos(rx)]])
    Ry = np.array([[np.cos(ry), 0, np.sin(ry)],
                   [0, 1, 0],
                   [-np.sin(ry), 0, np.cos(ry)]])
    Rz = np.array([[np.cos(rz), -np.sin(rz), 0],
                   [np.sin(rz), np.cos(rz), 0],
                   [0, 0, 1]])

    # Apply rotations
    rotated_coords = Rz @ (Ry @ (Rx @ coords))

    # Apply translation
    tx, ty, tz = translation
    rotated_coords[0, :] += tx
    rotated_coords[1, :] += ty
    rotated_coords[2, :] += tz

    # Reshape back to grid
    x_transformed = rotated_coords[0, :].reshape(h, w)
    y_transformed = rotated_coords[1, :].reshape(h, w)
    z_transformed = rotated_coords[2, :].reshape(h, w)

    return x_transformed, y_transformed, z_transformed, img

# Animation function
def update(frame):
    ax.cla()  # Clear the plot

    # Translation and rotation values
    translation = (np.sin(frame / 10), np.cos(frame / 10), np.sin(frame / 20))
    rotation = (frame % 360, frame % 360, frame % 360)

    # Transform the image
    x, y, z, img_transformed = transform_image(img, translation, rotation)

    # Plot the transformed image
    ax.plot_surface(x, y, z, rstride=1, cstride=1, facecolors=img_transformed, shade=False)

    # Set axis limits
    ax.set_xlim([-2, 2])
    ax.set_ylim([-2, 2])
    ax.set_zlim([-2, 2])

    ax.set_title("3D Image Movement and Rotation")

# Create the animation
ani = FuncAnimation(fig, update, frames=360, interval=50, repeat=True)

plt.show()
