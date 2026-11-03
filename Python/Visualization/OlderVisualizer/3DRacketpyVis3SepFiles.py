import os
import pyvista as pv
import pyvistaqt as pvqt
import numpy as np
import csv
from PIL import Image

import tkinter as tk
from tkinter import filedialog

# --- Utility to select file ---
def select_file():
    from tkinter import filedialog
    return filedialog.askopenfilename(title="Select a file", filetypes=[("all files", "*.*")])

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

# Constants
UPPER_ARM_LENGTH = 1.5
FOREARM_LENGTH = 1.5
RACKET_LENGTH = 0

# Fixed shoulder position (origin)
SHOULDER_POS = np.array([0.0, 0.0, 0.0])

# Load data for shoulder, elbow, and wrist angles
shoulder_angles_list = []
elbow_angles_list = []
wrist_angles_list = []

# Utility function to normalize angles to the range [0, 360)
def normalize_angle(angle):
    """Normalize an angle to the range [0, 360)."""
    return angle % 360

# Open file 1 for shoulder
filename = select_file()
with open(filename, 'r') as f:
    reader = csv.reader(f, delimiter=" ")
    for row in reader:
        try:
            shoulder_angles_list.append([
                normalize_angle(float(row[0]) + 360 if float(row[0]) < 0 else float(row[0])),  # Normalize row[0]
                normalize_angle(float(row[1]) + 360 if float(row[1]) < 0 else float(row[1])),  # Normalize row[1]
                normalize_angle(float(row[2]))  # Normalize row[2]
            ])
        except:
            print("bad data")
            continue  # Skip malformed rows

# Open file 2 for elbow
filename = select_file()
with open(filename, 'r') as f:
    reader = csv.reader(f, delimiter=" ")
    for row in reader:
        try:
            elbow_angles_list.append([
                normalize_angle(float(row[0]) + 360 if float(row[0]) < 0 else float(row[0])),  # Normalize row[0]
                normalize_angle(float(row[1]) + 360 if float(row[1]) < 0 else float(row[1])),  # Normalize row[1]
                normalize_angle(float(row[2]))  # Normalize row[2]
            ])
        except:
            print("bad data")
            continue  # Skip malformed rows

# Open file 3 for wrist
filename = select_file()
with open(filename, 'r') as f:
    reader = csv.reader(f, delimiter=" ")
    for row in reader:
        try:
            wrist_angles_list.append([
                normalize_angle(float(row[0]) + 360 if float(row[0]) < 0 else float(row[0])),  # Normalize row[0]
                normalize_angle(float(row[1]) + 360 if float(row[1]) < 0 else float(row[1])),  # Normalize row[1]
                normalize_angle(float(row[2]))  # Normalize row[2]
            ])
        except:
            print("bad data")
            continue  # Skip malformed rows

# Combine angles into frames
frames = list(zip(shoulder_angles_list, elbow_angles_list, wrist_angles_list))

# Initialize angles
frame_index = 0
shoulder_angles, elbow_angles, wrist_angles = frames[frame_index]

# Function to compute joint positions
def compute_positions(shoulder_angles, elbow_angles, wrist_angles):
    """Compute positions of elbow, wrist, and racket based on joint angles."""

    # Normalize angles
    shoulder_angles = [normalize_angle(a) for a in shoulder_angles]
    elbow_angles = [normalize_angle(a) for a in elbow_angles]
    wrist_angles = [normalize_angle(a) for a in wrist_angles]

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
plotter.add_mesh(upper_line, color="black", line_width=12, name="UpperArm")
plotter.add_mesh(forearm_line, color="black", line_width=12, name="Forearm")
#plotter.add_mesh(racket_line, color="green", line_width=4, name="Racket")

# Create joint markers
shoulder_marker_actor = plotter.add_mesh(pv.Sphere(radius=0.05), color="red", name="Shoulder")
elbow_marker_actor = plotter.add_mesh(pv.Sphere(radius=0.05), color="blue", name="Elbow")

shoulder_marker_actor.SetPosition(*SHOULDER_POS)
elbow_marker_actor.SetPosition(*elbow_pos)
# wrist_marker_actor.SetPosition(*wrist_pos)

# # Create plane for the image
# image_plane = pv.Plane(center=(0, 0.5, 0), direction=(0, 0, 1), i_size=1, j_size=1)  # Adjust center to connect handle
# image_plane.rotate_z(180)  # Rotate the plane to align the handle correctly
# image_plane_actor = plotter.add_mesh(image_plane, texture=image_texture, name="ImagePlane")

# 3D Racket Geometry (replaces image plane)
handle_length = 0.8
handle_radius = 0.05
head_outer_radius = 0.5
head_inner_radius = 0.45
head_segments = 64
num_strings = 8
string_radius = 0.005
#handle cylinder for handle
handle = pv.Cylinder(center=(0, .3, 0),
                     direction=(0, 1, 0),
                     radius=handle_radius,
                     height=handle_length)
handle.translate([0, -handle_length/2, 0])  # pivot at handle base

rim_outer = pv.Cylinder(center=(0, 1.2, 0),
                        direction=(0, 0, 1),
                        radius=head_outer_radius,
                        height=0.1,
                        resolution=head_segments).triangulate()

rim_inner = pv.Cylinder(center=(0, 1.2, 0),
                        direction=(0, 0, 1),
                        radius=head_inner_radius,
                        height=head_inner_radius * 2,
                        resolution=head_segments).triangulate()

head_rim = rim_outer.boolean_difference(rim_inner)
head_rim.rotate_x(90)
head_rim.translate([0, -handle_length/2, 0])



########## possible new code to fix string lines in previous section

strings = []
y_offset = 1.2  # match the center of the racket head along Y


# Vertical strings (along Z axis)
######## makes it show up correctly but in the wrong axis ###


x_vals = np.linspace(-head_inner_radius * 0.9, head_inner_radius * 0.9, num_strings)
for x in x_vals:
    max_x = np.sqrt(head_inner_radius**2 - x**2)
    line = pv.Cylinder(center=(x, y_offset, 0),
                       direction=(0, 1, 0),  # along Y
                       radius=string_radius,
                       height=2*max_x)
    strings.append(line)

# Horizontal strings (along X axis)
y_vals = np.linspace(-head_inner_radius * 0.9, head_inner_radius * 0.9, num_strings)
for y in y_vals:
    max_y = np.sqrt(head_inner_radius**2 - y**2)
    line = pv.Cylinder(center=(0, y + y_offset, 0),
                       direction=(1, 0, 0),  # along X
                       radius=string_radius,
                       height=2*max_y)
    strings.append(line)

# Combine all strings
string_mesh = pv.MultiBlock(strings).combine()
racket = handle + head_rim + string_mesh
racket_actor = plotter.add_mesh(racket, color='royalblue', smooth_shading=True, name="Racket")

############ end of new strings code ##########
### end of racket geometry ###

# Function to interpolate positions
def interpolate_positions(start, end, num_points=10):
    """Interpolate positions between two points."""
    line = pv.Line(start, end, resolution=num_points - 1)
    return line.points

# Precompute interpolated positions for all frames
interpolated_frames = []
num_points = 20  # Adjust this value based on desired smoothness
for i in range(len(frames)):
    current_angles = frames[i]
    next_angles = frames[(i + 1) % len(frames)]

    # Compute joint positions for current and next frames
    current_elbow, current_wrist, current_racket_end = compute_positions(*current_angles)
    next_elbow, next_wrist, next_racket_end = compute_positions(*next_angles)

    # Interpolate positions
    interpolated_elbow = interpolate_positions(current_elbow, next_elbow, num_points)
    interpolated_wrist = interpolate_positions(current_wrist, next_wrist, num_points)
    interpolated_racket = interpolate_positions(current_racket_end, next_racket_end, num_points)

    # Store interpolated positions
    interpolated_frames.append((interpolated_elbow, interpolated_wrist, interpolated_racket))

# Update function with precomputed interpolation
interpolation_index = 0  # Track the current interpolation step
def update_scene():
    global frame_index, interpolation_index

    # Get precomputed interpolated positions for the current frame
    interpolated_elbow, interpolated_wrist, interpolated_racket = interpolated_frames[frame_index]

    # Update line positions with the current interpolated point
    upper_line.points[1] = interpolated_elbow[interpolation_index]
    forearm_line.points[0] = interpolated_elbow[interpolation_index]
    forearm_line.points[1] = interpolated_wrist[interpolation_index]
    # racket_line.points[0] = interpolated_wrist[interpolation_index]
    # racket_line.points[1] = interpolated_racket[interpolation_index]

    elbow_marker_actor.SetPosition(*interpolated_elbow[interpolation_index])
    racket_actor.SetPosition(*interpolated_wrist[interpolation_index])  # Connect handle to forearm

    plotter.update()  # Update the plotter for smooth animation

    # Move to the next interpolation step
    interpolation_index += 1
    if interpolation_index >= len(interpolated_elbow):  # If the end of interpolation is reached
        interpolation_index = 0
        frame_index = (frame_index + 1) % len(interpolated_frames)  # Move to the next frame

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
plotter.add_callback(update_scene, interval=10)  # Runs update_scene every 50ms

# Keep window open
plotter.app.exec_()
