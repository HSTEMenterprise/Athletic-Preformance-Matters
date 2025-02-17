import bluetooth

# Replace with the device name of your ESP32
target_name = "ESP32"
target_address = None

print("Searching for devices...")

# Search for nearby Bluetooth devices
nearby_devices = bluetooth.discover_devices(duration=8, lookup_names=True, lookup_class=False)

for addr, name in nearby_devices:
    try:
        print(f"Found Bluetooth device: {name} - {addr}")
        if name == target_name:
            target_address = addr
            print(f"Target device {name} found with address {addr}")
            break
    except UnicodeEncodeError:
        print(f"Error encoding name {name} for device at address {addr}")

if target_address is None:
    print(f"Could not find target Bluetooth device {target_name}")
else:
    # Connect to the device
    print(f"Connecting to {target_name} at {target_address}")
try:
    # Port 1 is typically used for Serial Port Profile (SPP) communication
    port = 1
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((target_address, port))
    print(f"Connected to {target_name}")

    # Read data continuously
    print("Receiving data...")
    while True:
        data = sock.recv(1024)  # Read up to 1024 bytes
        print(f"Received: {data.decode('utf-8')}")
except bluetooth.btcommon.BluetoothError as e:
    print(f"Bluetooth error: {e}")
except KeyboardInterrupt:
    print("Disconnected")
finally:
    sock.close()
