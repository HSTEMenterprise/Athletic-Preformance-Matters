from PIL import Image
import sys
import numpy as np
import matplotlib.pyplot as plt
import time
import csv

from matplotlib.widgets import Slider
import tkinter as tk
from tkinter import filedialog

def select_file():
    file_path = filedialog.askopenfilename(title="Select a file", filetypes=[("all files", "*.*")])
    return file_path if file_path else None

filename = select_file()

data = []
with open(filename, 'r') as file:
    reader = csv.reader(file, delimiter=' ')
    for row in reader:
        cleaned_row = [float(value) for value in row if value]
        data.append(cleaned_row)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

shoulder_angle = [0, 0, 0]

def draw_player(shoulder_angle):
    ax.cla()  # Clear the axes
    shoulder = np.array([0, 0, 0])
    elbow = shoulder + np.array([
        np.sin(np.radians(shoulder_angle[0])),
        np.sin(np.radians(shoulder_angle[1])),
        np.sin(np.radians(shoulder_angle[2]))
    ])
    elbow = elbow / np.linalg.norm(elbow)
    
    # Draw the shoulder-to-elbow line
    ax.plot([shoulder[0], elbow[0]], [shoulder[1], elbow[1]], [shoulder[2], elbow[2]], color='blue', linewidth=6)
    
    ax.set_xlim([-2, 2])
    ax.set_ylim([-2, 2])
    ax.set_zlim([-2, 2])
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Shoulder to Elbow Animation')

i = [0]

draw_player(data[i[0]])
plt.ion()
plt.show()

while True:
    if i[0] < len(data) - 1:
        i[0] += 1
        print(data[i[0]])
        draw_player(data[i[0]])
        plt.draw()
        plt.pause(0.01)
    else:
        break
