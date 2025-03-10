import os
import pyvista as pv
import pyvistaqt as pvqt
import numpy as np
import csv

import tkinter as tk
from tkinter import filedialog

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
UPPER_ARM_LENGTH = 1.0
FOREARM_LENGTH = 1.0
RACKET_LENGTH = 0.8

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
racket_line = pv.Line(wrist_pos, racket_end_pos)

# Add lines
plotter.add_mesh(upper_line, color="brown", line_width=4, name="UpperArm")
plotter.add_mesh(forearm_line, color="brown", line_width=4, name="Forearm")
plotter.add_mesh(racket_line, color="green", line_width=4, name="Racket")

# Create joint markers
shoulder_marker_actor = plotter.add_mesh(pv.Sphere(radius=0.01), color="red", name="Shoulder")
elbow_marker_actor = plotter.add_mesh(pv.Sphere(radius=0.01), color="blue", name="Elbow")
wrist_marker_actor = plotter.add_mesh(pv.Sphere(radius=0.01), color="blue", name="Wrist")

shoulder_marker_actor.SetPosition(*SHOULDER_POS)
elbow_marker_actor.SetPosition(*elbow_pos)
wrist_marker_actor.SetPosition(*wrist_pos)

# Update function
def update_scene():
    global frame_index, elbow_angle, wrist_angle

    # Get current frame data (shoulder angles)
    shoulder_angles = np.array(frames[frame_index])

    # Compute new joint positions
    new_elbow, new_wrist, new_racket_end = compute_positions(shoulder_angles, elbow_angle, wrist_angle)

    # Update line positions
    upper_line.points[1] = new_elbow
    forearm_line.points[0] = new_elbow
    forearm_line.points[1] = new_wrist
    racket_line.points[0] = new_wrist
    racket_line.points[1] = new_racket_end

    elbow_marker_actor.SetPosition(*new_elbow)
    wrist_marker_actor.SetPosition(*new_wrist)

    # Move to next frame
    frame_index = (frame_index + 1) % len(frames)

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
plotter.add_callback(update_scene, interval=50)  # Runs update_scene every 50ms

# Keep window open
plotter.app.exec_()
