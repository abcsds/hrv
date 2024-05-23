import asyncio
from bleak import BleakScanner

# Define the addresses, names, and UUIDs of devices
devices = [
    {"address": "DB:6E:5B:87:4E:50", "name": "Polar H10", "uuid": "00002a37-0000-1000-8000-00805f9b34fb"},
    {"address": "DE:C5:AC:14:25:28", "name": "HR6 0039090", "uuid": "00002a37-0000-1000-8000-00805f9b34fb"},
    {"address": "CD:4B:39:D5:62:36", "name": "HR-70ECAB5D", "uuid": "00002a37-0000-1000-8000-00805f9b34fb"},
    {"address": "CB:1E:40:C8:F6:03", "name": "HR-70EC985D", "uuid": "00002a37-0000-1000-8000-00805f9b34fb"},
    {"address": "DB:D1:1C:A1:57:3D", "name": "HR-70EC845D", "uuid": "00002a37-0000-1000-8000-00805f9b34fb"},
    {"address": "FF:D2:0F:F3:FE:EC", "name": "HR-70ECE75D", "uuid": "00002a37-0000-1000-8000-00805f9b34fb"},
    {"address": "E8:9B:59:E2:8C:71", "name": "HR-70ECD35D", "uuid": "00002a37-0000-1000-8000-00805f9b34fb"},
    {"address": "F2:48:B2:FF:3E:CE", "name": "HR-70ECD05D", "uuid": "00002a37-0000-1000-8000-00805f9b34fb"},
]

async def main():
    found = False
    matched = []
    while found == False:
        found_devices = await BleakScanner.discover()
        found = False
        for d in found_devices:
            # print(f"{d.name}: {d.address}")
            ads = [device["address"] for device in devices]
            if d.address in ads:
                found += 1
                matched.append(d)
                print("*", end="", flush=True)
            else:
                print(".", end="", flush=True)
        print()
    print(f"{found} devices found:")
    for match in matched:
        print(f"    {match.name}: {match.address}")
    
    return devices


devices = asyncio.run(main())
found = False