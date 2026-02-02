import os
import pyvista as pv
import pyvistaqt as pvqt
import numpy as np
import csv
from PIL import Image

import tkinter as tk
from tkinter import filedialog

# open racket image file
# --- Utility to select file ---
def select_file():
    from tkinter import filedialog
    return filedialog.askopenfilename(title="Select a file", filetypes=[("all files", "*.*")])

# --- Load image and prepare texture (facecolors) ---
filename = select_file()
image = Image.open(filename)
image_texture = pv.numpy_to_texture(np.array(image))

# open csv file(s)
def select_file():
    initial_dir = os.path.abspath("../Data/")
    file_path = filedialog.askopenfilename(
            title="Select a file",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*")),
            initialdir = initial_dir
    )
    if file_path:
        return file_path

filename = select_file()



# Constants
UPPER_ARM_LENGTH = 0.5
FOREARM_LENGTH = 0.5
RACKET_LENGTH = 0

# Fixed shoulder position (origin)
SHOULDER_POS = np.array([0.0, 0.0, 0.0])

# Load CSV data (Expecting: shoulder_angle_x, shoulder_angle_y, shoulder_angle_z,
# elbow_angle_x, elbow_angle_y, elbow_angle_z,
# wrist_angle_x, wrist_angle_y, wrist_angle_z)
frames = []
with open(filename, 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        try:
            shoulder_angles = [float(row[0]), float(row[1]), float(row[2])]
            elbow_angles = [float(row[3]), float(row[4]), float(row[5])]
            wrist_angles = [float(row[6]), float(row[7]), float(row[8])]
        except:
            continue  # Skip malformed rows
        frames.append((shoulder_angles, elbow_angles, wrist_angles))

# If no data, create dummy oscillating movement
if not frames:
    t = np.linspace(0, 2*np.pi, 100)
    frames = [
        (
            [30*np.sin(x), 30*np.cos(x), 15*np.sin(2*x)],  # Shoulder angles
            [45*np.sin(x), 45*np.cos(x), 20*np.sin(2*x)],  # Elbow angles
            [60*np.sin(x), 60*np.cos(x), 25*np.sin(2*x)]   # Wrist angles
        )
        for x in t
    ]

# Initialize angles
frame_index = 0
shoulder_angles, elbow_angles, wrist_angles = frames[frame_index]

# Function to compute joint positions
def compute_positions(shoulder_angles, elbow_angles, wrist_angles):
    """Compute positions of elbow, wrist, and racket based on joint angles."""

    # Convert angles to radians
    shoulder_rad = np.radians(shoulder_angles)
    elbow_rad = np.radians(elbow_angles)
    wrist_rad = np.radians(wrist_angles)

    # Compute elbow position (shoulder -> elbow direction)
    elbow_pos = SHOULDER_POS + np.array([
        UPPER_ARM_LENGTH * np.cos(shoulder_rad[0]) * np.cos(shoulder_rad[1]),
        UPPER_ARM_LENGTH * np.sin(shoulder_rad[0]) * np.cos(shoulder_rad[1]),
        UPPER_ARM_LENGTH * np.sin(shoulder_rad[1])
    ])

    # Compute wrist position (elbow -> wrist direction)
    wrist_pos = elbow_pos + np.array([
        FOREARM_LENGTH * np.cos(elbow_rad[0]) * np.cos(elbow_rad[1]),
        FOREARM_LENGTH * np.sin(elbow_rad[0]) * np.cos(elbow_rad[1]),
        FOREARM_LENGTH * np.sin(elbow_rad[1])
    ])

    # Compute racket position (wrist -> racket direction)
    racket_end_pos = wrist_pos + np.array([
        RACKET_LENGTH * np.cos(wrist_rad[0]) * np.cos(wrist_rad[1]),
        RACKET_LENGTH * np.sin(wrist_rad[0]) * np.cos(wrist_rad[1]),
        RACKET_LENGTH * np.sin(wrist_rad[1])
    ])

    return elbow_pos, wrist_pos, racket_end_pos

# Compute initial joint positions
elbow_pos, wrist_pos, racket_end_pos = compute_positions(shoulder_angles, elbow_angles, wrist_angles)

# Create PyVista plotter
plotter = pvqt.BackgroundPlotter()
plotter.set_background("white")

# Create arm and racket meshes
upper_line = pv.Line(SHOULDER_POS, elbow_pos)
forearm_line = pv.Line(elbow_pos, wrist_pos)
#racket_line = pv.Line(wrist_pos, racket_end_pos)

# Add lines
plotter.add_mesh(upper_line, color="brown", line_width=4, name="UpperArm")
plotter.add_mesh(forearm_line, color="brown", line_width=4, name="Forearm")
#plotter.add_mesh(racket_line, color="green", line_width=4, name="Racket")

# Create joint markers
shoulder_marker_actor = plotter.add_mesh(pv.Sphere(radius=0.01), color="red", name="Shoulder")
elbow_marker_actor = plotter.add_mesh(pv.Sphere(radius=0.01), color="blue", name="Elbow")

shoulder_marker_actor.SetPosition(*SHOULDER_POS)
elbow_marker_actor.SetPosition(*elbow_pos)
# wrist_marker_actor.SetPosition(*wrist_pos)

# Create plane for the image
image_plane = pv.Plane(center=(0, 0.5, 0), direction=(0, 0, 1), i_size=1, j_size=1)  # Adjust center to connect handle
image_plane.rotate_z(180)  # Rotate the plane to align the handle correctly
image_plane_actor = plotter.add_mesh(image_plane, texture=image_texture, name="ImagePlane")

# Function to interpolate positions
def interpolate_positions(start, end, num_points=10):
    """Interpolate positions between two points."""
    line = pv.Line(start, end, resolution=num_points - 1)
    return line.points

# Update function with interpolation
def update_scene():
    global frame_index

    # Get current and next frame data (angles)
    current_angles = frames[frame_index]
    next_frame_index = (frame_index + 1) % len(frames)
    next_angles = frames[next_frame_index]

    # Compute joint positions for current and next frames
    current_elbow, current_wrist, current_racket_end = compute_positions(*current_angles)
    next_elbow, next_wrist, next_racket_end = compute_positions(*next_angles)

    # Interpolate positions
    interpolated_elbow = interpolate_positions(current_elbow, next_elbow)
    interpolated_wrist = interpolate_positions(current_wrist, next_wrist)
    interpolated_racket = interpolate_positions(current_racket_end, next_racket_end)

    # Update line positions with interpolated points
    for i in range(len(interpolated_elbow)):
        upper_line.points[1] = interpolated_elbow[i]
        forearm_line.points[0] = interpolated_elbow[i]
        forearm_line.points[1] = interpolated_wrist[i]
        # racket_line.points[0] = interpolated_wrist[i]
        # racket_line.points[1] = interpolated_racket[i]

        elbow_marker_actor.SetPosition(*interpolated_elbow[i])
        image_plane_actor.SetPosition(*interpolated_wrist[i])  # Connect handle to forearm

        plotter.update()  # Update the plotter for smooth animation

    # Move to next frame
    frame_index = next_frame_index

# # Slider callbacks
# def on_elbow_slider(value):
#     global elbow_angle
#     elbow_angle = value
#     update_scene()

# def on_wrist_slider(value):
#     global wrist_angle
#     wrist_angle = value
#     update_scene()

# # Add sliders
# plotter.add_slider_widget(on_elbow_slider, [0.0, 180.0], value=elbow_angle, title="Elbow Angle",
#                           pointa=(0.025, 0.1), pointb=(0.31, 0.1))
# plotter.add_slider_widget(on_wrist_slider, [0.0, 180.0], value=wrist_angle, title="Wrist Angle",
#                           pointa=(0.025, 0.05), pointb=(0.31, 0.05))

# Start animation loop
plotter.add_callback(update_scene, interval=25)  # Runs update_scene every 50ms

# Keep window open
plotter.app.exec_()
