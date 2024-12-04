from PIL import Image
import sys
import numpy as np
import matplotlib.pyplot as plt
import time
import csv

from matplotlib.widgets import Slider
from mpl_toolkits.mplot3d import axes3d
import matplotlib.image as mpimg

import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog

def select_file():
    file_path = filedialog.askopenfilename(title="select a file", filetypes=[("all files", "*.*")])
    if file_path:
        return file_path

filename = select_file()

#import csv
data = []
with open(filename, 'r') as file:
    reader = csv.reader(file, delimiter = ' ')
    for row in reader:
        cleaned_row = [float(value) for value in row if value]
        data.append(cleaned_row)


x = np.arange(len(data))
y = [point[1] for point in data]  # Extracting the second column for y values

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
    shoulder = np.array([0, 0, 0])

    elbow = shoulder + np.array([np.sin(np.radians(shoulder_angle[0])),
                                 np.sin(np.radians(shoulder_angle[1])),
                                 np.sin(np.radians(shoulder_angle[2])),
                                 ])
    elbow = elbow / np.linalg.norm(elbow)
    wrist = elbow + np.array([np.cos(np.radians(elbow_angle)),
                              np.sin(np.radians(elbow_angle)),
                              0])
    racket = wrist + np.array([np.cos(np.radians(wrist_angle)),
                               np.sin(np.radians(wrist_angle)),
                               0.5])  # Racket is above wrist

    # Draw the arms
    ax.plot([shoulder[0], elbow[0]], [shoulder[1], elbow[1]], [shoulder[2], elbow[2]], color='blue', linewidth=6)
    ax.plot([elbow[0], wrist[0]], [elbow[1], wrist[1]], [elbow[2], wrist[2]], color='blue', linewidth=6)

    ax.plot([0, 0], [0, 0], [0, -1], color='green', linewidth=8)  # Body

    # Set limits and labels
    ax.set_xlim([-2, 2])
    ax.set_ylim([-2, 2])
    ax.set_zlim([-2, 2])
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('3D Tennis Player Animation')

# Slider setup
axcolor = 'lightgoldenrodyellow'
ax_slider_elbow = plt.axes([0.1, 0.05, 0.65, 0.03], facecolor=axcolor)
ax_slider_wrist = plt.axes([0.1, 0.09, 0.65, 0.03], facecolor=axcolor)

slider_elbow = Slider(ax_slider_elbow, 'Elbow Angle', -90, 90, valinit=elbow_angle)
slider_wrist = Slider(ax_slider_wrist, 'Wrist Angle', -90, 90, valinit=wrist_angle)

plt.ion()
plt.show()

i = [0]

firstShoulderPos = data[i[0]]

# Initial draw
draw_player(data[i[0]], elbow_angle, wrist_angle)

def handle_close():
    sys.exit()

def handle_open_file(data):
    filename = select_file()
    if filename:
        with open(filename, 'r') as file:
            reader = csv.reader(file, delimiter=' ')
            for row in reader:
                cleaned_row = [float(value) for value in row if value]
                data.append(cleaned_row)
        print("File loaded successfully!")
        root.destroy()

while True:
    if i[0] < len(data) - 1:
        i[0] += 1
        print(data[i[0]])
        draw_player(data[i[0]], slider_elbow.val, slider_wrist.val)
        plt.draw()
        plt.pause(0.01)
    else:
        # Main application
        data = []  # List to store the loaded data

        root = tk.Tk()
        root.title("Choose an Option")
        root.geometry("300x150")

        # Add buttons
        close_button = tk.Button(root, text="Close", command=handle_close)
        close_button.pack(pady=10)

        open_file_button = tk.Button(root, text="Open a New File", command=lambda: handle_open_file(data))
        open_file_button.pack(pady=10)

        # Start the GUI loop
        root.mainloop()
