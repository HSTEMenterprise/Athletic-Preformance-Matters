import numpy as np
import csv

def axis_angle(axis, angle_rad):
    ax, ay, az = axis / np.linalg.norm(axis)
    s = np.sin(angle_rad / 2)
    return np.array([np.cos(angle_rad / 2), ax*s, ay*s, az*s])

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

def write_quat_csv(path, quats):
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['wW', 'wX', 'wY', 'wZ'])
        for q in quats:
            w.writerow([f"{q[0]:.5f}", f"{q[1]:.5f}", f"{q[2]:.5f}", f"{q[3]:.5f}"])

N = 300
t = np.linspace(0, 1, N)

# Shoulder: compound rotation — pitch forward about Z, then roll up about X
shoulder = []
for i in range(N):
    ramp = np.sin(np.pi * t[i])**2
    q_pitch = axis_angle([0, 0, 1], np.radians(-90 * ramp))   # swings arm forward (+X -> +Z... actually toward -Y depending on sign)
    q_roll  = axis_angle([1, 0, 0], np.radians(45 * ramp))     # lifts arm
    shoulder.append(q_mul(q_roll, q_pitch))                    # pitch first, then roll

# Elbow: bends during swing
elbow = [axis_angle([0, 1, 0], np.radians(60 * np.sin(np.pi * t[i])**2)) for i in range(N)]

# Wrist: forehand snap at the end
wrist_angle = np.zeros(N)
for i in range(N):
    if t[i] < 0.6:
        wrist_angle[i] = 0.0
    elif t[i] < 0.85:
        frac = (t[i] - 0.6) / 0.25
        wrist_angle[i] = np.radians(-30 * frac)
    else:
        frac = (t[i] - 0.85) / 0.15
        wrist_angle[i] = np.radians(-30 + 90 * frac)
wrist = [axis_angle([1, 0, 0], wrist_angle[i]) for i in range(N)]

write_quat_csv("test_shoulder.csv", shoulder)
write_quat_csv("test_elbow.csv", elbow)
write_quat_csv("test_wrist.csv", wrist)
print("Wrote 3 test CSVs,", N, "frames each")