import numpy as np
import pyvista as pv
import csv
import tkinter as tk
from tkinter import filedialog

# Function to select a file
def select_file():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(title="Select a file", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
    return file_path if file_path else None

# Load CSV Data
filename = select_file()
data = []

if filename:
    with open(filename, 'r') as file:
        reader = csv.reader(file, delimiter=' ')
        for row in reader:
            cleaned_row = [float(value) for value in row if value]
            data.append(cleaned_row)

# Initialize PyVista Plotter
plotter = pv.Plotter()
plotter.set_background("black")

# Initial Joint Positions
shoulder = np.array([0, 0, 0])
elbow = np.array([1, 0, 0])  # Default position before animation

# Create Line Mesh (Shoulder to Elbow)
line = pv.Line(shoulder, elbow)

# Add the 3D Line to the Scene
actor = plotter.add_mesh(line, color="blue", line_width=6)

# Set Axis Limits
plotter.camera_position = "xy"
plotter.add_axes()
plotter.show_grid()
plotter.show(auto_close=False)

# Animation Loop
for angles in data:
    shoulder_angle = np.radians(angles)  # Convert degrees to radians
    elbow = shoulder + np.array([
        np.sin(shoulder_angle[0]),
        np.sin(shoulder_angle[1]),
        np.sin(shoulder_angle[2])
    ])
    elbow = elbow / np.linalg.norm(elbow)

    # Update Line
    line.points = np.array([shoulder, elbow])
    plotter.update()  # Refresh PyVista scene

    # Small Delay for Animation
    plotter.app.processEvents()

plotter.close()
