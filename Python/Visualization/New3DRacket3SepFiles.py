import os
import pyvista as pv
import pyvistaqt as pvqt
import numpy as np
import math
import csv
import tkinter as tk
from tkinter import filedialog
import vtk
import sys
from qtpy.QtWidgets import QApplication

## -- File functions --

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

# --- Data Loading ---
def load_quat_csv(path):
    """Load BNO055 w,x,y,z CSV -> list of normalized world quaternions."""
    out = []
    with open(path, 'r') as f:
        reader = csv.reader(f, delimiter=",")
        header = next(reader, None)          # skip 'wW,wX,wY,wZ' header!
        for i, row in enumerate(reader):
            if not row or len(row) < 4:
                continue                      # handles your blank lines
            try:
                q = np.array([float(v) for v in row[:4]])
            except ValueError:
                print(f"bad data at row {i+2}: {row}")
                continue
            n = np.linalg.norm(q)
            if n < 1e-6:
                continue
            out.append(q / n)
    return out


# ---------- Quaternion math (numpy only, no scipy dependency) ----------
def q_normalize(q):
    n = np.linalg.norm(q)
    if n < 1e-12:
        return np.array([1.0, 0.0, 0.0, 0.0])
    return q / n

# define multiplication as hamilton product
def q_mul(a, b):
    """Hamilton product, q = (w, x, y, z)."""
    aw, ax, ay, az_ = a
    bw, bx, by, bz = b
    return np.array([
        aw*bw - ax*bx - ay*by - az_*bz,
        aw*bx + ax*bw + ay*bz - az_*by,
        aw*by - ax*bz + ay*bw + az_*bx,
        aw*bz + ax*by - ay*bx + az_*bw,
    ])

def q_conj(q):
    return np.array([q[0], -q[1], -q[2], -q[3]])

def q_rotate(q, v):
    """Rotate vector v by quaternion q."""
    vq = np.array([0.0, v[0], v[1], v[2]])
    return q_mul(q_mul(q, vq), q_conj(q))[1:]

def q_slerp(a, b, t):
    """Shortest-path spherical interpolation -> constant-length limbs."""
    a, b = q_normalize(a), q_normalize(b)
    d = float(np.dot(a, b))
    if d < 0.0:            # take shortest arc
        b = -b
        d = -d
    if d > 0.9995:         # nearly identical -> lerp is fine
        r = a + t * (b - a)
        return q_normalize(r)
    theta_0 = np.arccos(d)
    theta = theta_0 * t
    s0 = np.sin(theta_0 - theta) / np.sin(theta_0)
    s1 = np.sin(theta) / np.sin(theta_0)
    return q_normalize(s0 * a + s1 * b)

#get quaternion from euler angle
def quat_from_euler(roll, pitch, yaw):
    """ZYX intrinsic, radians -> (w,x,y,z)"""
    cr, sr = np.cos(roll/2),  np.sin(roll/2)
    cp, sp = np.cos(pitch/2), np.sin(pitch/2)
    cy, sy = np.cos(yaw/2),   np.sin(yaw/2)
    return np.array([
        cy*cp*cr + sy*sp*sr,
        cy*cp*sr - sy*sp*cr,
        cy*sp*cr + sy*cp*sr,
        sy*cp*cr - cy*sp*sr,
    ])

#quaternions to euler angles
def quat_to_euler(q):
    """Convert quaternion (w,x,y,z) to ZYX Euler angles (yaw, pitch, roll) in radians."""
    w, x, y, z = q
    # Roll (X-axis rotation)
    sinr_cosp = 2 * (w * x + y * z)
    cosr_cosp = 1 - 2 * (x * x + y * y)
    roll = np.arctan2(sinr_cosp, cosr_cosp)
    
    # Pitch (Y-axis rotation)
    sinp = 2 * (w * y - z * x)
    pitch = np.arcsin(np.clip(sinp, -1, 1))
    
    # Yaw (Z-axis rotation)
    siny_cosp = 2 * (w * z + x * y)
    cosy_cosp = 1 - 2 * (y * y + z * z)
    yaw = np.arctan2(siny_cosp, cosy_cosp)
    
    return yaw, pitch, roll  # Z, Y, X order

# matrix math 
def q_to_matrix(q):
    w, x, y, z = q_normalize(q)
    return np.array([
        [1-2*(y*y+z*z),   2*(x*y-w*z),   2*(x*z+w*y)],
        [  2*(x*y+w*z), 1-2*(x*x+z*z),   2*(y*z-w*x)],
        [  2*(x*z-w*y),   2*(y*z+w*x), 1-2*(x*x+y*y)],
    ])

def place_actor(actor, pos, q_rot=None):
    if q_rot is None:
        return

    w = float(q_rot[0])
    v = np.asarray(q_rot[1:], dtype=float)
    s = float(np.linalg.norm(v))
    if s < 1e-9:
        angle, axis = (180.0, (1.0, 0.0, 0.0)) if w < 0 else (0.0, (1.0, 0.0, 0.0))
    else:
        angle = float(np.degrees(2.0 * np.arctan2(s, w)))
        axis = tuple(v / s)

    xf = vtk.vtkTransform()
    xf.Translate(pos[0], pos[1], pos[2])  # translation first
    xf.RotateWXYZ(angle, *axis)             # then rotation
    actor.SetUserTransform(xf)


# -- Code: Load data, create geometry, define animation logic, display everything
# Load Quaternion Data
print("Select Shoulder CSV...")
# shoulder_file = select_file()
shoulder_file = r"C:\Users\storm\Documents\Python\H-stem\test_shoulder.csv"
shoulder_quats_list = load_quat_csv(shoulder_file)

print("Select Elbow CSV...")
# elbow_file = select_file()
elbow_file = r"C:\Users\storm\Documents\Python\H-stem\test_elbow.csv"
elbow_quats_list = load_quat_csv(elbow_file)

print("Select Wrist CSV...")
# wrist_file = select_file()
wrist_file = r"C:\Users\storm\Documents\Python\H-stem\test_wrist.csv"
wrist_quats_list = load_quat_csv(wrist_file)

# Check if data loaded!
if not (shoulder_quats_list and elbow_quats_list and wrist_quats_list):
    raise ValueError("Not enough data loaded. Please select valid CSV files.")

# Combine frames into list (WARN if not all same length for each data file)
lens = [len(shoulder_quats_list), len(elbow_quats_list), len(wrist_quats_list)]
print(f"INFO: sample counts S/E/W = {lens}")
if len(set(lens)) != 1:
    print(f"WARN: unequal lengths; truncating all to {min(lens)} frames")
frames = list(zip(shoulder_quats_list, elbow_quats_list, wrist_quats_list))
num_frames = len(frames)

# --- Geometry Creation ---

# Ball joints

# Body Constants (in meters) arms+racket
UPPER_ARM_LENGTH = 0.4 # average male 0.426
FOREARM_LENGTH = 0.245 # average male - 0.254 female: 0.235
RACKET_LENGTH = 0.69 #standard tennis racket size 0.686 - 0.699
RACKET_HANDLE_LENGTH = 0.19 # standard handle length (rest is 0.5 then)
RACKET_HEAD_RADIUS = 0.12

# Body constants cont.
#avg hip width: male/female: 29.1cm/29.6cm we'll just take 0.29m as our width of body cylinder
BODY_WIDTH = 0.29
BODY_LENGTH = 0.42 # men/w 0.457/0.4 (hip to neck) (from c7 vertebra to bottom of the neck)
HEAD_RADIUS = 0.11 # head chin to top: men/w 0.231/0.218 (I took 0.22/2 = 0.11 for radius)
SHOULDER_HEIGHT = 1.22 # average shoulder height of male/female: 1.24 m to 1.445 m/1.24 m to 1.33 m
NECK_LENGTH = 0.05 # gap between shoulder (top of body) and head

#Legs
LEG_LENGTH = 0.8 #hip to floor: 0.83/0.79 m/w
LEG_RADIUS = 0.06 # (REDUCED) 0.08 is for a thigh circumference of 0.5m

# Fixed shoulder position (above Origin (+z))
SHOULDER_POS = np.array([0, -BODY_WIDTH/2, SHOULDER_HEIGHT]) 

# misc element constants Body bottom to top
BODY_SPHERE_R = BODY_LENGTH/3
BODY_CYLINDER_L = (2*BODY_LENGTH)/3
BODY_CONE_L = NECK_LENGTH #Neck

# 1. Figure (Lines + Shapes)
upper_line = pv.Line(SHOULDER_POS, SHOULDER_POS + np.array([UPPER_ARM_LENGTH, 0, 0]))
forearm_line = pv.Line(SHOULDER_POS, SHOULDER_POS + np.array([FOREARM_LENGTH, 0, 0]))

# Body -> sphere + cylinder 
body_sphere = pv.Sphere(radius=BODY_SPHERE_R, center = (0, 0, LEG_LENGTH + BODY_SPHERE_R))
body_cylinder = pv.Cylinder(center=(0, 0, LEG_LENGTH + BODY_SPHERE_R + BODY_CYLINDER_L/2), direction = (0, 0, 1), radius=BODY_WIDTH/2, height=BODY_CYLINDER_L)

# Neck & Head-> cone with flat top for head (sphere) to sit on
body_cone = pv.Cone(center=(0, 0, LEG_LENGTH + BODY_SPHERE_R + BODY_CYLINDER_L + BODY_CONE_L/2), direction = (0, 0, 1), radius=BODY_WIDTH/2, height=BODY_CONE_L)
head = pv.Sphere(radius=HEAD_RADIUS, center = (0, 0, SHOULDER_HEIGHT + HEAD_RADIUS))

# Legs -> Cylinders Center (0, y, z) y should be end of torso (add spheres at knees?) 
left_leg = pv.Cylinder(center=(0, -BODY_WIDTH/2 + LEG_RADIUS, LEG_LENGTH/2), direction = (0, 0, 1), radius=LEG_RADIUS, height=LEG_LENGTH)  
right_leg = pv.Cylinder(center=(0, BODY_WIDTH/2 - LEG_RADIUS, LEG_LENGTH/2), direction = (0, 0, 1), radius=LEG_RADIUS, height=LEG_LENGTH) 

#feet -> half cylinders with spheres at each end


# 2. Racket Geometry (Built once, moved every frame)

# Handle: axis along +X with base at origin, end at x = HANDLE_LENGTH
handle = pv.Cylinder(center=(RACKET_HANDLE_LENGTH/2, 0, 0), 
                     direction=(1, 0, 0), 
                     radius=0.0175, # avg circumference of handle is 0.11cm so radius should be 0.0175
                     height=RACKET_HANDLE_LENGTH)

# Head of racket: disc centered at origin first, rotate, then move handle to end
head_rim = pv.Cylinder(center=(RACKET_HANDLE_LENGTH + RACKET_HEAD_RADIUS, 0, 0), 
                       direction=(0, 0, 1), 
                       radius=RACKET_HEAD_RADIUS, 
                       height=0.03, 
                       resolution=32).triangulate()
head_rim.rotate_x(90) # so now it's in the XY plane
racket = handle + head_rim

# Calculate the bounding box center and shift everything by that amount
bbox = racket.bounds
bbox_center_x = (bbox[0] + bbox[1]) / 2  # min x and max x
racket.translate([-bbox_center_x, 0, 0])
# Now bbox center is at x = 0 (the handle base)

# 3. Joint Markers
shoulder_sphere = pv.Sphere(radius=0.05)
elbow_sphere = pv.Sphere(radius=0.05)
wrist_sphere = pv.Sphere(radius=0.05)

# --- Animation Logic ---

REST_DIR = np.array([1.0, 0.0, 0.0])   # limb points +X when unrotated

# Compute positions from quaternions
def compute_positions(q_shoulder, q_elbow, q_wrist):
    """
    q_shoulder : upper-arm orientation in world frame
    q_elbow    : forearm orientation relative to upper arm  (see note below)
    q_wrist    : racket orientation relative to forearm
    """
    elbow_pos  = SHOULDER_POS + UPPER_ARM_LENGTH  * q_rotate(q_shoulder, REST_DIR)

    q_forearm  = q_mul(q_shoulder, q_elbow)       # compose parent -> child
    wrist_pos  = elbow_pos + FOREARM_LENGTH * q_rotate(q_forearm, REST_DIR)

    q_racket   = q_mul(q_forearm, q_wrist)        # full racket attitude
    racket_end = wrist_pos + RACKET_LENGTH * q_rotate(q_racket, REST_DIR)

    return elbow_pos, wrist_pos, racket_end, q_racket

# Reference pose functions: Create and apply reference functions 
def apply_reference(frames, refs):
    """Convert absolute world quats -> rest-frame + relative chain."""
    out = []
    for qs, qe, qw in frames:
        s_rel = q_mul(q_conj(refs['shoulder']), qs)
        e_rel = q_mul(q_conj(qs), qe)      # pure elbow flexion
        w_rel = q_mul(q_conj(qe), qw)      # pure wrist motion
        out.append((s_rel, e_rel, w_rel))
    return out

def capture_reference(frames, n=30):
    """Mean of first n samples, hemisphere-aligned."""
    refs = {}
    for i, name in enumerate(('shoulder', 'elbow', 'wrist')):
        qs = [f[i] for f in frames[:n]]
        ref0 = qs[0]
        aligned = [q if np.dot(q, ref0) >= 0 else -q for q in qs]
        q = np.mean(aligned, axis=0)
        refs[name] = q / np.linalg.norm(q)
    return refs

# Run reference functions
refs = capture_reference(frames)
frames = apply_reference(frames, refs)
print("INFO: reference captured from first", len(frames[:30]), "samples")

# --- Setup PyVista ---
plotter = pvqt.BackgroundPlotter()
## Set background
plotter.set_background("grey", top='white')
plotter.window_size = (1200, 800) # Set window size

# Add floor
plotter.add_floor()

# Add Meshes 
# Arms
plotter.add_mesh(upper_line, color="black", line_width=10, name="UpperArm")
plotter.add_mesh(forearm_line, color="black", line_width=10, name="Forearm")

#Body
plotter.add_mesh(body_sphere, color="white", name="Bodysphere")
plotter.add_mesh(body_cylinder, color="orange", name="Bodycylinder")
plotter.add_mesh(body_cone, color="orange", name="Bodycone")
plotter.add_mesh(head, color="brown", name="Head")

plotter.add_mesh(left_leg, color="black", line_width=10, name="Leftleg")
plotter.add_mesh(right_leg, color="black", line_width=10, name="Rightleg")


# Add Markers
shoulder_actor = plotter.add_mesh(shoulder_sphere, color="red", name="Shoulder")
elbow_actor = plotter.add_mesh(elbow_sphere, color="blue", name="Elbow")
wrist_actor = plotter.add_mesh(wrist_sphere, color="green", name="Wrist")

# Add Racket
racket_actor = plotter.add_mesh(racket, color='royalblue', smooth_shading=True, name="Racket")

# --- Animation Loop ---
frame_index = 0
interpolation_index = 0

def update_scene():
    global frame_index, interpolation_index

    # if frame_index == 0:  # debug only print first frame
    #     elbow_pos, wrist_pos, racket_end, q_racket = compute_positions(frames[0][0], frames[0][1], frames[0][2])
    #     print("ELBOW:", elbow_pos)
    #     print("WRIST:", wrist_pos)
    #     print("RACKET_END:", racket_end)
    #     print("RACKET_Q:", q_racket)

    # Get current frame angles
    s_ang, e_ang, w_ang = frames[frame_index]
    
    # Compute positions
    elbow_pos, wrist_pos, racket_end, q_racket = compute_positions(s_ang, e_ang, w_ang)
    
    # Update Line Geometry (Vertices)
    # Upper Arm: Shoulder -> Elbow
    upper_line.points[0] = SHOULDER_POS
    upper_line.points[1] = elbow_pos
    
    # Forearm: Elbow -> Wrist
    forearm_line.points[0] = elbow_pos
    forearm_line.points[1] = wrist_pos
    
    # Update Markers
    place_actor(shoulder_actor, SHOULDER_POS)
    place_actor(elbow_actor, elbow_pos)
    place_actor(wrist_actor, wrist_pos)
    
    # Update Racket Position
    place_actor(racket_actor, wrist_pos, q_racket)

    # Move to next frame
    frame_index = (frame_index + 1) % num_frames
    plotter.update()

# Start the loop
# interval in milliseconds (10ms = 100 FPS)
plotter.add_callback(update_scene, interval=10)
plotter.show()
app = QApplication.instance() or QApplication(sys.argv)
sys.exit(app.exec_())