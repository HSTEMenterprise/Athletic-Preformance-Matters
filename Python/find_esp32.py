import asyncio
from bleak import BleakScanner
from bleak.exc import BleakDBusError

# Global scanner lock
scanner_lock = asyncio.Lock()

async def find_esp32(target_name="ESP32"):
    async with scanner_lock:  # Ensure no concurrent scans
        print("Ensuring no active BLE scans before starting...")
        
        # Stop any existing scanner instance (workaround for BlueZ errors)
        try:
            scanner = BleakScanner()
            await scanner.stop()  # Ensure no previous scans are running
        except Exception as e:
            print(f"⚠️ Warning: Could not stop previous scanner: {e}")

        print("Scanning for BLE devices...")
        try:
            devices = await BleakScanner.discover()  # Perform BLE scan

            found = False
            for device in devices:
                print(f"Found device: {device.name} - {device.address}")
                if device.name and target_name in device.name:
                    print(f"✅ Target device '{device.name}' found with address: {device.address}")
                    found = True
                    break  # Stop searching once found

            if not found:
                print(f"❌ Could not find target device '{target_name}'. Ensure it is advertising.")

        except BleakDBusError as e:
            print(f"❌ BLE scan failed due to BlueZ error: {e}")
            print("Retrying in 5 seconds...")
            await asyncio.sleep(5)
            await find_esp32(target_name)  # Retry scan

# Run the async function
asyncio.run(find_esp32())
