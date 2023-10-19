import asyncio
from bleak import BleakClient
from helperfuncs import interpret


# Define the addresses, names, and UUIDs of devices
devices = [
    {"address": "DB:6E:5B:87:4E:50", "name": "Polar H10", "uuid": "00002a37-0000-1000-8000-00805f9b34fb"},
    {"address": "DE:C5:AC:14:25:28", "name": "HR6 0039090", "uuid": "00002a37-0000-1000-8000-00805f9b34fb"},
    {"address": "CD:4B:39:D5:62:36", "name": "HR-70ECAB5D", "uuid": "00002a37-0000-1000-8000-00805f9b34fb"},
    {"address": "CB:1E:40:C8:F6:03", "name": "HR-70EC985D", "uuid": "00002a37-0000-1000-8000-00805f9b34fb"},
    {"address": "DB:D1:1C:A1:57:3D", "name": "HR-70EC845D", "uuid": "00002a37-0000-1000-8000-00805f9b34fb"},

    {"address": "CD:4B:39:D5:62:36", "name": "HR-70ECAB5D", "uuid": "00002a37-0000-1000-8000-00805f9b34fb"},
    {"address": "CD:4B:39:D5:62:36", "name": "HR-70ECAB5D", "uuid": "00002a37-0000-1000-8000-00805f9b34fb"},
    {"address": "CD:4B:39:D5:62:36", "name": "HR-70ECAB5D", "uuid": "00002a37-0000-1000-8000-00805f9b34fb"},
]

device = devices[2]
print(f"Connecting to {device['name']}")
address = device["address"]
HR_UUID = device["uuid"]

def callback(sender: int, data: bytearray):
    if data:
        data = interpret(data)
        print(f"HR: {data['hr']}", end=" ")
        if "rr" in data.keys():
            print("Fonud RR:")
            for data_rr in data["rr"]:
                print(f"    RR: {data_rr}")
        return data
    else:
        return None

async def main(address):
    client = BleakClient(address)
    try:
        await client.connect()
        print(f"Device Address: {client.address}")
        hr = await client.start_notify(HR_UUID, callback)
        while True:
            await asyncio.sleep(1)
    except Exception as e:
        print(f"Exeption: {e}")
    except KeyboardInterrupt:
        print(f"Stopped by user")
        await client.stop_notify(HR_UUID)
    finally:
        await client.disconnect()

asyncio.run(main(address))