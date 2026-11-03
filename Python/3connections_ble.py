'''
Author: Oliver, Bella, Sawyer
Date: 11/16/25
Last Updated: 2/13/26
Purpose: Connecting to the ESP32 via Blutooth and saving data to a csv file
'''

import asyncio
import csv
from datetime import date
from bleak import BleakClient, BleakScanner
import uuid
import sys

# UUID's of Shoulder, elbow, and wrist sensors
SHOULDER_UUID = "f06a5de9-5c7e-4b20-aef9-c120fb6711e4"
SHOULDER_C_UUID = "f2181a7e-86de-4c6f-8d0d-1df47cadcd30"

ELBOW_UUID = "da16f14a-c4c6-11f0-8de9-0242ac120002"
ELBOW_C_UUID = "da16f370-c4c6-11f0-8de9-0242ac120002"

WRIST_UUID = "f6024b44-c65f-11f0-8de9-0242ac120002"
WRIST_C_UUID = "004dac4c-c660-11f0-8de9-0242ac120002"

# 3 columns for each sensor organized: Shoulder elbow wrist
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


MAX_DATAPOINTS = 100
NUM_COLLECTED = 0

async def sensorComms(uuid, c_uuid, body_part, csv_file):
    global NUM_COLLECTED
    print(f"INFO: Scanning for {body_part} sensor...")
    devices = await BleakScanner.discover(return_adv=True)
    esp32 = None
    for d, a in devices.values():
        if a.service_uuids and a.service_uuids[0] == uuid:
            esp32 = d
            break

    if not esp32:
        print(f"ERROR: {body_part} sensor not found.")
        return

    print(f"INFO: Connecting to {esp32.address}...")
    async with BleakClient(esp32.address) as client:
        print("INFO: Connected.")

        def handle_notification(_, data):
            global NUM_COLLECTED
            if NUM_COLLECTED > MAX_DATAPOINTS-1:
                print("INFO: collected 100 data points. Exiting...")
                sys.exit(0)
            decoded_data = data.split(b'\x00')[0].decode("ascii").strip()
            if decoded_data == "waiting":
                return
            #print(decoded_data)
            append_to_csv_file(csv_file, decoded_data.split(" "))  
            NUM_COLLECTED += 1

        await client.start_notify(c_uuid, handle_notification)
        print("=== Receiving data... (press Ctrl+C to stop) ===")
        await asyncio.sleep(60)
        await client.stop_notify(c_uuid)


## CSV file for each sensor (shoulder, elbow and wrist)
async def main():
    
    ## Define each CSV file
    shoulder = create_new_csv_file('shoulder')
    elbow = create_new_csv_file('elbow')
    wrist = create_new_csv_file('wrist')

    ## Run our bluetooth function with asyncio.gather(3 times!) with shoulder, elbow, and wrist UUIDs and c UUID's and also which body part it is
    await asyncio.gather(
        sensorComms(SHOULDER_UUID, SHOULDER_C_UUID, "shoulder", shoulder),
        sensorComms(ELBOW_UUID, ELBOW_C_UUID, "elbow", elbow),
        sensorComms(WRIST_UUID, WRIST_C_UUID, "wrist", wrist)
    )

if __name__ == "__main__":
    asyncio.run(main())
    print(f"INFO: Saved sensor data.")
