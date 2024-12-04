import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.widgets import Slider
import cv2

# Function to apply rotation matrix
def apply_rotation(x, y, z, angles):
    """Rotate points by given angles (in degrees)."""
    rx, ry, rz = np.radians(angles)
    # Rotation matrices
    R_x = np.array([[1, 0, 0],
                    [0, np.cos(rx), -np.sin(rx)],
                    [0, np.sin(rx), np.cos(rx)]])
    R_y = np.array([[np.cos(ry), 0, np.sin(ry)],
                    [0, 1, 0],
                    [-np.sin(ry), 0, np.cos(ry)]])
    R_z = np.array([[np.cos(rz), -np.sin(rz), 0],
                    [np.sin(rz), np.cos(rz), 0],
                    [0, 0, 1]])
    R = R_z @ R_y @ R_x  # Combine rotations
    coords = np.vstack([x.ravel(), y.ravel(), z.ravel()])
    rotated_coords = R @ coords
    return rotated_coords[0].reshape(x.shape), rotated_coords[1].reshape(y.shape), rotated_coords[2].reshape(z.shape)

# Load tennis racket image
img = cv2.imread('../Assets/racket.png')[:, :, ::-1]  # Convert BGR to RGB if loaded with cv2
img = img / 255.0  # Normalize image

# 3D visualization setup
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Initial angles and position
shoulder_angle = [0, 0, 0]
elbow_angle = 0
wrist_angle = 0

def draw_player(shoulder_angle, elbow_angle, wrist_angle):
    ax.cla()  # Clear the plot

    # Compute joint positions
    shoulder = np.array([0, 0, 0])
    elbow = shoulder + np.array([np.sin(np.radians(shoulder_angle[0])),
                                 np.sin(np.radians(shoulder_angle[1])),
                                 np.sin(np.radians(shoulder_angle[2]))])
    elbow = elbow / np.linalg.norm(elbow)
    wrist = elbow + np.array([np.cos(np.radians(elbow_angle)),
                              np.sin(np.radians(elbow_angle)),
                              0])
    racket = wrist + np.array([0, 0, 0.5])  # Racket position relative to wrist

    # Define racket surface
    racket_width = 0.3
    racket_height = 0.5
    x = np.array([[-racket_width / 2, racket_width / 2], [-racket_width / 2, racket_width / 2]])
    y = np.array([[-racket_height / 2, -racket_height / 2], [racket_height / 2, racket_height / 2]])
    z = np.array([[0, 0], [0, 0]])

    # Rotate the racket surface based on wrist angle
    x_rot, y_rot, z_rot = apply_rotation(x, y, z, [0, 0, wrist_angle])
    x_rot += racket[0]
    y_rot += racket[1]
    z_rot += racket[2]

    # Plot arm
    ax.plot([shoulder[0], elbow[0]], [shoulder[1], elbow[1]], [shoulder[2], elbow[2]], color='blue', linewidth=6)
    ax.plot([elbow[0], wrist[0]], [elbow[1], wrist[1]], [elbow[2], wrist[2]], color='blue', linewidth=6)

    # Plot racket
    ax.plot_surface(x_rot, y_rot, z_rot, facecolors=img, shade=False)

    # Set limits
    ax.set_xlim([-2, 2])
    ax.set_ylim([-2, 2])
    ax.set_zlim([-2, 2])
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('3D Tennis Racket Visualization')

# Slider setup
axcolor = 'lightgoldenrodyellow'
slider_elbow = Slider(plt.axes([0.1, 0.05, 0.65, 0.03], facecolor=axcolor), 'Elbow Angle', -90, 90, valinit=elbow_angle)
slider_wrist = Slider(plt.axes([0.1, 0.09, 0.65, 0.03], facecolor=axcolor), 'Wrist Angle', -90, 90, valinit=wrist_angle)

# Real-time update loop
plt.ion()
while True:
    elbow_angle = slider_elbow.val
    wrist_angle = slider_wrist.val
    draw_player(shoulder_angle, elbow_angle, wrist_angle)
    plt.draw()
    plt.pause(0.01)
