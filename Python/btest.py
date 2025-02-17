import asyncio
from bleak import BleakScanner

async def scan_ble_devices():
    print("Scanning for BLE devices...")
    devices = await BleakScanner.discover()
    if devices:
        print("Found the following devices:")
        for i, device in enumerate(devices, start=1):
            print(f"{i}. {device.name or 'Unknown'} ({device.address})")
    else:
        print("No BLE devices found.")

if __name__ == "__main__":
    asyncio.run(scan_ble_devices())
