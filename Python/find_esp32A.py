import asyncio
from bleak import BleakScanner, BleakClient
from bleak.exc import BleakDBusError, BleakError

# Global scanner lock
scanner_lock = asyncio.Lock()

# Notification handler
def notification_handler(uuid):
    def handler(sender, data):
        print(f"🔔 Notification from {uuid}: {data} (hex: {data.hex()})")
    return handler

async def find_esp32_and_read_all(target_name="ESP32"):
    async with scanner_lock:
        print("Ensuring no active BLE scans before starting...")
        
        try:
            scanner = BleakScanner()
            await scanner.stop()
        except Exception as e:
            print(f"⚠️ Warning: Could not stop previous scanner: {e}")

        print("Scanning for BLE devices...")
        try:
            devices = await BleakScanner.discover()
            target_device = None

            for device in devices:
                print(f"Found device: {device.name} - {device.address}")
                if device.name and target_name in device.name:
                    target_device = device
                    print(f"✅ Target device '{device.name}' found at address: {device.address}")
                    break

            if not target_device:
                print(f"❌ Could not find target device '{target_name}'. Ensure it is advertising.")
                return

            async with BleakClient(target_device) as client:
                if not client.is_connected:
                    print("❌ Failed to connect to the ESP32.")
                    return

                print("🔗 Connected to ESP32. Retrieving services...")
                services = await client.get_services()

                for service in services:
                    print(f"\n📡 Service {service.uuid} - {service.description}")
                    for char in service.characteristics:
                        props = ', '.join(char.properties)
                        print(f"  🔸 Characteristic {char.uuid} ({props})")

                        if "read" in char.properties:
                            try:
                                value = await client.read_gatt_char(char.uuid)
                                print(f"    📥 Read Value: {value} (hex: {value.hex()})")
                            except Exception as e:
                                print(f"    ⚠️ Could not read: {e}")

                        if "notify" in char.properties:
                            try:
                                await client.start_notify(char.uuid, notification_handler(char.uuid))
                                print(f"    ✅ Subscribed to notifications.")
                            except Exception as e:
                                print(f"    ⚠️ Could not subscribe to notifications: {e}")

                print("\n📡 Listening for notifications... Press Ctrl+C to exit.")
                while True:
                    await asyncio.sleep(1)

        except BleakDBusError as e:
            print(f"❌ BLE scan failed due to BlueZ error: {e}")
            print("Retrying in 5 seconds...")
            await asyncio.sleep(5)
            await find_esp32_and_read_all(target_name)

        except BleakError as e:
            print(f"❌ Failed to connect or read: {e}")

        except asyncio.CancelledError:
            print("🔌 Disconnected.")
        except KeyboardInterrupt:
            print("🛑 Exiting...")

# Run the async function
asyncio.run(find_esp32_and_read_all())
