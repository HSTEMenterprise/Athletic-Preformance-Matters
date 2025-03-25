import time
import random
from datetime import datetime

# Parameters
num_steps = 500             # How many coordinate sets to generate
step_delay = 0.1           # Time between steps in seconds
max_step = 0.2             # Maximum movement per step

# Initialize three 3D points
points = [
    [random.uniform(-1, 1) for _ in range(3)],
    [random.uniform(-1, 1) for _ in range(3)],
    [random.uniform(-1, 1) for _ in range(3)],
]

for _ in range(num_steps):
    # Smoothly update each point
    for point in points:
        for i in range(3):
            delta = random.uniform(-max_step, max_step)
            point[i] += delta

    # Get the current timestamp
    timestamp = datetime.now().isoformat()

    # Print in the required format
    line = ' '.join(f"{coord:.3f}" for point in points for coord in point)
    print(f"{line} {timestamp}")

    # Optional delay to simulate real-time generation
    time.sleep(step_delay)
