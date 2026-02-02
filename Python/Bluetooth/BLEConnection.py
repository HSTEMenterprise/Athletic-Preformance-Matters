import argparse
import asyncio
import time

from bleak import BleakClient, BleakScanner

address = "D4:8A:FC:C9:CA:EA"

name = "ESP32"
characteristics = {"1": "e2f5435e-634f-44d3-9c7f-54bfe8c96e64", "2":  "0eb71bcb-eb31-4f19-88b9-116a4e52a2c4", "3":  "801b2ee2-e7b6-4aa8-ae2d-4e82b426d157" }
duration = "50000"
 
class DeviceNotFoundError(Exception):
    pass

async def run_ble_client(queues: dict):
    """Scans for the BLE device and starts notification for multiple characteristics."""
    print("Starting scan...")

#   //  if address:
#         device = await BleakScanner.find_device_by_address(address)
#         if device is None:
#             print("Could not find device with address '%s'", address)
#             raise DeviceNotFoundError
    if name:
        device = await BleakScanner.find_device_by_name(name)
        if device is None:
            print("Could not find device with name '%s'", name)
            raise DeviceNotFoundError

    print("Connecting to device...")

    async with BleakClient(device) as client:
        print("Connected!")

        async def callback_handler(characteristic, data):
            """Handles incoming BLE notifications."""
            timestamp = time.time()
            print(f"[{characteristic}] Received: {data}")  # Log to console
            await queues[characteristic].put((timestamp, data))  # Store in queue

        # Start notification for each characteristic
        tasks = []
        for characteristic in characteristics:
            queues[characteristic] = asyncio.Queue()
            await client.start_notify(characteristic, lambda c, d: callback_handler(c, d))
            print(f"Started notifications for {characteristic}")
        
        await asyncio.sleep(duration)  # Keep connection open for set time

        # Stop notifications
        for characteristic in characteristics:
            await client.stop_notify(characteristic)
            await queues[characteristic].put((time.time(), None))  # Exit signal
        
        print("Disconnected from BLE device.")

async def run_queue_consumer(queues: dict):
    """Consumes data from multiple BLE characteristic queues and logs it in real-time."""
    print("Starting queue consumer...")

    while True:
        for characteristic, queue in queues.items():
            try:
                epoch, data = await asyncio.wait_for(queue.get(), timeout=0.1)
                if data is None:
                    print(f"[{characteristic}] Stopping consumer...")
                    return
                else:
                    print(f"[{characteristic}] Processed data at {epoch}: {data}")
            except asyncio.TimeoutError:
                continue  # No data, continue checking other queues

async def main():
    queues = {}  # Dictionary to hold queues per characteristic
    client_task = run_ble_client(queues)
    consumer_task = run_queue_consumer(queues)

    try:
        await asyncio.gather(client_task, consumer_task)
    except DeviceNotFoundError:
        pass

    print("Main process done.")

if __name__ == "__main__":
    asyncio.run(main())
