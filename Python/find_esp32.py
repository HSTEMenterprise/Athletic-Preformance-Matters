import asyncio
from bleak import BleakScanner

async def find_esp32(target_name="ESP32"):
    print("Scanning for BLE devices...")
    devices = await BleakScanner.discover()
    
    found = False
    for device in devices:
        print(f"Found device: {device.name} - {device.address}")
        if device.name and target_name in device.name:
            print(f"✅ Target device '{device.name}' found with address: {device.address}")
            found = True
            break  # Stop searching once found

    if not found:
        print(f"❌ Could not find target device '{target_name}'. Ensure it is advertising.")

# Run the async function
asyncio.run(find_esp32())
