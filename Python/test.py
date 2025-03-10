from pydbus import SystemBus
import asyncio
from bleak import BleakScanner

async def scan_devices():
    print("Scanning for Bluetooth LE devices...")
    scanner = BleakScanner()
    await scanner.stop()  # Ensure no previous scans are running
    devices = await scanner.discover(passive=True)

    if not devices:
        print("❌ No devices found.")
    else:
        print("✅ Devices detected:")
        for device in devices:
            print(f"- {device.name} ({device.address})")


bus = SystemBus()
adapter = bus.get("org.bluez", "/org/bluez/hci0")

try:
    adapter.StopDiscovery()
    print("✅ Stopped any active BLE scans")
except Exception as e:
    print(f"⚠️ No active scans to stop: {e}")

asyncio.run(scan_devices())
