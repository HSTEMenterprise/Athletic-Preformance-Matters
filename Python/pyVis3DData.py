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

# Load CSV data (Expecting: shoulder_angle_x, shoulder_angle_y, shoulder_angle_z)
frames = []
with open(filename, 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        try:
            shoulder_angle_x = float(row[0])
            shoulder_angle_y = float(row[1])
            shoulder_angle_z = float(row[2])
        except:
            continue  # Skip malformed rows
        frames.append((shoulder_angle_x, shoulder_angle_y, shoulder_angle_z))

# If no data, create dummy oscillating movement
if not frames:
    t = np.linspace(0, 2*np.pi, 100)
    frames = [(30*np.sin(x), 30*np.cos(x), 15*np.sin(2*x)) for x in t]

# Initialize angles
frame_index = 0
shoulder_angles = np.array(frames[frame_index])
elbow_angle = 90.0
wrist_angle = 180.0

# Function to compute joint positions
def compute_positions(shoulder_angles, elbow_deg, wrist_deg):
    """Compute positions of elbow, wrist, and racket based on joint angles."""

    # Convert angles to radians
    shoulder_rad = np.radians(shoulder_angles)
    elbow_rad = np.radians(elbow_deg)
    wrist_rad = np.radians(wrist_deg)

    # Compute elbow position (shoulder -> elbow direction)
    elbow_pos = SHOULDER_POS + np.array([
        UPPER_ARM_LENGTH * np.cos(shoulder_rad[0]) * np.cos(shoulder_rad[1]),
        UPPER_ARM_LENGTH * np.sin(shoulder_rad[0]) * np.cos(shoulder_rad[1]),
        UPPER_ARM_LENGTH * np.sin(shoulder_rad[1])
    ])

    # Compute wrist position (elbow -> wrist direction)
    forearm_angle = np.radians(180.0 - elbow_deg)
    wrist_pos = elbow_pos + np.array([
        FOREARM_LENGTH * np.cos(forearm_angle) * np.cos(shoulder_rad[2]),
        FOREARM_LENGTH * np.sin(forearm_angle) * np.cos(shoulder_rad[2]),
        FOREARM_LENGTH * np.sin(shoulder_rad[2])
    ])

    # Compute racket position (wrist -> racket direction)
    racket_angle = forearm_angle + np.radians(180.0 - wrist_deg)
    racket_end_pos = wrist_pos + np.array([
        RACKET_LENGTH * np.cos(racket_angle),
        RACKET_LENGTH * np.sin(racket_angle),
        0.0
    ])

    return elbow_pos, wrist_pos, racket_end_pos

# Compute initial joint positions
elbow_pos, wrist_pos, racket_end_pos = compute_positions(shoulder_angles, elbow_angle, wrist_angle)

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
    global frame_index, elbow_angle, wrist_angle

    # Get current and next frame data (shoulder angles)
    current_angles = np.array(frames[frame_index])
    next_frame_index = (frame_index + 1) % len(frames)
    next_angles = np.array(frames[next_frame_index])

    # Compute joint positions for current and next frames
    current_elbow, current_wrist, current_racket_end = compute_positions(current_angles, elbow_angle, wrist_angle)
    next_elbow, next_wrist, next_racket_end = compute_positions(next_angles, elbow_angle, wrist_angle)

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

# Slider callbacks
def on_elbow_slider(value):
    global elbow_angle
    elbow_angle = value
    update_scene()

def on_wrist_slider(value):
    global wrist_angle
    wrist_angle = value
    update_scene()

# Add sliders
plotter.add_slider_widget(on_elbow_slider, [0.0, 180.0], value=elbow_angle, title="Elbow Angle",
                          pointa=(0.025, 0.1), pointb=(0.31, 0.1))
plotter.add_slider_widget(on_wrist_slider, [0.0, 180.0], value=wrist_angle, title="Wrist Angle",
                          pointa=(0.025, 0.05), pointb=(0.31, 0.05))

# Start animation loop
plotter.add_callback(update_scene, interval=25)  # Runs update_scene every 50ms

# Keep window open
plotter.app.exec_()