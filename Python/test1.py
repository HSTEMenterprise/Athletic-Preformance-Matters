import asyncio
from bleak import BleakScanner

async def test_bleak():
    print("Starting BleakScanner...")
    scanner = BleakScanner()
    await scanner.start()
    await asyncio.sleep(5)  # Allow time for discovery
    devices = await scanner.get_discovered_devices()
    await scanner.stop()

    if devices:
        print("✅ Found devices:")
        for device in devices:
            print(f"- {device.name} ({device.address})")
    else:
        print("❌ No devices found.")

asyncio.run(test_bleak())
