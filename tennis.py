import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from mpl_toolkits.mplot3d import Axes3D

# Set up the figure and 3D axes
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Initialize joint angles
shoulder_angle = 0
elbow_angle = 0
wrist_angle = 0

# Function to draw the player
def draw_player(shoulder_angle, elbow_angle, wrist_angle):
    ax.cla()  # Clear the axes

    # Define joint positions based on angles
    shoulder = np.array([0, 0, 0])
    elbow = shoulder + np.array([np.cos(np.radians(shoulder_angle)),
                                 np.sin(np.radians(shoulder_angle)),
                                 0])
    wrist = elbow + np.array([np.cos(np.radians(elbow_angle)),
                              np.sin(np.radians(elbow_angle)),
                              0])
    racket = wrist + np.array([np.cos(np.radians(wrist_angle)),
                               np.sin(np.radians(wrist_angle)),
                               0.5])  # Racket is above wrist

    # Draw the arms
    ax.plot([shoulder[0], elbow[0]], [shoulder[1], elbow[1]], [shoulder[2], elbow[2]], color='blue', linewidth=6)
    ax.plot([elbow[0], wrist[0]], [elbow[1], wrist[1]], [elbow[2], wrist[2]], color='blue', linewidth=6)
    ax.plot([wrist[0], racket[0]], [wrist[1], racket[1]], [wrist[2], racket[2]], color='red', linewidth=3)  # Racket

    # Draw the body
    ax.plot([0, 0], [0, 0], [0, -1], color='green', linewidth=8)  # Body

    # Set limits and labels
    ax.set_xlim([-2, 2])
    ax.set_ylim([-2, 2])
    ax.set_zlim([-2, 2])
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('3D Tennis Player Animation')

# Initial draw
draw_player(shoulder_angle, elbow_angle, wrist_angle)

# Slider setup
axcolor = 'lightgoldenrodyellow'
ax_slider_shoulder = plt.axes([0.1, 0.01, 0.65, 0.03], facecolor=axcolor)
ax_slider_elbow = plt.axes([0.1, 0.05, 0.65, 0.03], facecolor=axcolor)
ax_slider_wrist = plt.axes([0.1, 0.09, 0.65, 0.03], facecolor=axcolor)

slider_shoulder = Slider(ax_slider_shoulder, 'Shoulder Angle', -180, 180, valinit=shoulder_angle)
slider_elbow = Slider(ax_slider_elbow, 'Elbow Angle', -90, 90, valinit=elbow_angle)
slider_wrist = Slider(ax_slider_wrist, 'Wrist Angle', -90, 90, valinit=wrist_angle)

# Update function for sliders
def update(val):
    shoulder_angle = slider_shoulder.val
    elbow_angle = slider_elbow.val
    wrist_angle = slider_wrist.val
    draw_player(shoulder_angle, elbow_angle, wrist_angle)
    plt.draw()

# Connect sliders to the update function
slider_shoulder.on_changed(update)
slider_elbow.on_changed(update)
slider_wrist.on_changed(update)

plt.show()
