'''
Author: Sawyer + Others
Date: 2025ish
Last Updated: 2/2/2026
Purpose: Visualizer on pyvis for 3D data (shoulder, elbow, wrist angles) with image texture
'''

import os
import pyvista as pv            #for 3D geometry and visualization data
import pyvistaqt as pvqt        
import numpy as np
import csv
from PIL import Image
import tkinter as tk            
from tkinter import filedialog

# CSV file selecton
def select_file():
    initial_dir = os.path.abspath("../Data/")
    file_path = filedialog.askopenfilename(
            title="Select a CSV file",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*")),
            initialdir=initial_dir
    )
    if file_path:
        return file_path

filename = select_file()

# Constants form arm length
UPPER_ARM_LENGTH = 1.5
FOREARM_LENGTH = 1.5
RACKET_LENGTH = 0  # unkown fully what this does. Used in line 77 to compute wrist position?
SHOULDER_POS = np.array([0.0, 0.0, 0.0])  # Fixed shoulder position (origin)

# Load CSV data, expecting angles for shoulder, elbow, wrist. Data in csv file is in 9 seperate columns.
frames = []
with open(filename, 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        try:
            shoulder_angles = [float(row[5]), float(row[6]), float(row[7])]    #row numbers can be ajusted based on where the data is in the csv file.
            elbow_angles = [float(row[8]), float(row[9]), float(row[10])]
            wrist_angles = [float(row[11]), float(row[12]), float(row[13])]
        except:
            continue                                                           #skips bad/missing data
        frames.append((shoulder_angles, elbow_angles, wrist_angles))         #stores it for animation later

#initialize frame
frame_index = 0
shoulder_angles, elbow_angles, wrist_angles = frames[frame_index]

# Compute joint positions
def compute_positions(shoulder_angles, elbow_angles, wrist_angles):
    # Coverting angles from degrees to radians
    shoulder_rad = np.radians(shoulder_angles)
    elbow_rad = np.radians(elbow_angles)
    wrist_rad = np.radians(wrist_angles)
# elbow positions from shoulder
    elbow_pos = SHOULDER_POS + np.array([
        UPPER_ARM_LENGTH * np.cos(shoulder_rad[0]) * np.cos(shoulder_rad[1]),
        UPPER_ARM_LENGTH * np.sin(shoulder_rad[0]) * np.cos(shoulder_rad[1]),
        UPPER_ARM_LENGTH * np.sin(shoulder_rad[1])
    ])
# wrist positions from elbow
    wrist_pos = elbow_pos + np.array([
        FOREARM_LENGTH * np.cos(elbow_rad[0]) * np.cos(elbow_rad[1]),
        FOREARM_LENGTH * np.sin(elbow_rad[0]) * np.cos(elbow_rad[1]),
        FOREARM_LENGTH * np.sin(elbow_rad[1])
    ])
#racket tip from wrist? Unknown fully what this is
    racket_end_pos = wrist_pos + np.array([
        RACKET_LENGTH * np.cos(wrist_rad[0]) * np.cos(wrist_rad[1]),
        RACKET_LENGTH * np.sin(wrist_rad[0]) * np.cos(wrist_rad[1]),
        RACKET_LENGTH * np.sin(wrist_rad[1])
    ])

    return elbow_pos, wrist_pos, racket_end_pos
#position for first frame
elbow_pos, wrist_pos, racket_end_pos = compute_positions(shoulder_angles, elbow_angles, wrist_angles)

# Create PyVista plotter 
plotter = pvqt.BackgroundPlotter()
plotter.set_background("white")

# --- Camera orientation ---
plotter.camera.position = (0, 5, 0)   # look from +Y toward origin
#plotter.camera.focal_point = (0, 0, 0)
plotter.camera.up = (1, 0, 0)         # +X is "up"
plotter.camera_set = True

plotter.show_grid(bounds=[-2, 2, -2, 3, -2, 2])
###### new code 
# Create a 3D axes mesh
'''axes = pv.Axes(show_actor=True, line_width=5)

# Add to plotter
plotter.add_mesh(axes.actor)

plotter.show()
########## end new code
'''
# Arm segments
upper_line = pv.Line(SHOULDER_POS, elbow_pos)
forearm_line = pv.Line(elbow_pos, wrist_pos)
plotter.add_mesh(upper_line, color="brown", line_width=4, name="UpperArm")
plotter.add_mesh(forearm_line, color="brown", line_width=4, name="Forearm")

# Joint markers as little spheres
shoulder_marker_actor = plotter.add_mesh(pv.Sphere(radius=0.05), color="red", name="Shoulder")
elbow_marker_actor = plotter.add_mesh(pv.Sphere(radius=0.05), color="blue", name="Elbow")
shoulder_marker_actor.SetPosition(*SHOULDER_POS)
elbow_marker_actor.SetPosition(*elbow_pos)

# Add legend
plotter.add_legend(
    labels=[
        ["Red = Shoulder Joint", "red"],
        ["Blue = Elbow Joint", "blue"],
    ],
    bcolor="white",   # legend background
    border=True,
  
)

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




# --- Helper: interpolate between frames ---
def interpolate_positions(start, end, num_points=10):
    line = pv.Line(start, end, resolution=num_points - 1)
    return line.points

# --- Animation update ---
def update_scene():
    global frame_index

    current_angles = frames[frame_index]
    next_frame_index = (frame_index + 1) % len(frames)
    next_angles = frames[next_frame_index]

    current_elbow, current_wrist, _ = compute_positions(*current_angles)
    next_elbow, next_wrist, _ = compute_positions(*next_angles)

    interpolated_elbow = interpolate_positions(current_elbow, next_elbow)
    interpolated_wrist = interpolate_positions(current_wrist, next_wrist)

    for i in range(len(interpolated_elbow)):
        upper_line.points[1] = interpolated_elbow[i]
        forearm_line.points[0] = interpolated_elbow[i]
        forearm_line.points[1] = interpolated_wrist[i]

        elbow_marker_actor.SetPosition(*interpolated_elbow[i])
        racket_actor.SetPosition(*interpolated_wrist[i])  # ADDED racket moves with wrist

        plotter.update()

    frame_index = next_frame_index

# --- Start animation ---
plotter.add_callback(update_scene, interval=200)
plotter.app.exec_()