## This program should write to the proper columns depending on the input to the function

# 3 columns for each sensor organized: Shoulder elbow wrist
import asyncio
import csv
from datetime import date
import time

# One file for each sensor, x, y, z for each file
def create_new_csv_file(body_part) -> str:
    """Create a fresh CSV file and return a unique filename."""
    name = f"{body_part}-xyz-data-{date.today().strftime('%Y-%m-%d')}.csv"
    field_names = ["x", "y", "z"]
    with open(name, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=field_names)
        writer.writeheader()
    return name

def append_to_csv_file(file_name, data):
    with open(file_name, "a") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(data)

## CSV file for each sensor (shoulder, elbow and wrist)
async def main():
    
    ## Define each CSV file
    print("Creating new CSV files...")
    shoulder = create_new_csv_file('shoulder')
    elbow = create_new_csv_file('elbow')
    wrist = create_new_csv_file('wrist')
    

    ## Run our bluetooth function with asyncio.gather(3 times!) with shoulder, elbow, and wrist UUIDs and c UUID's and also which body part it is
    await asyncio.gather (
        append_to_csv_file(shoulder, [time.time(), "2", "3"]),
        append_to_csv_file(elbow, [time.time(), "5", "6"]),
        append_to_csv_file(wrist, [time.time(), "8", "9"])
    )

if __name__ == "__main__":
    asyncio.run(main())
    print(f"INFO: Saved sensor data.")