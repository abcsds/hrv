import asyncio
from bleak import BleakClient
from pylsl import StreamInfo, StreamOutlet
from helperfuncs import interpret

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
device = devices[3]
address = device["address"]
HR_UUID = device["uuid"]

info_hr = StreamInfo(name='HR',
    type='Markers',
    channel_count=1,
    channel_format='int32',
    source_id='HR_markers'
)
info_rr = StreamInfo(name='RR',
    type='Markers',
    channel_count=1,
    channel_format='int32',
    source_id='RR_markers'
)
outlet_hr = StreamOutlet(info_hr)
outlet_rr = StreamOutlet(info_rr)

def callback(sender: int, data: bytearray):
    if data:
        data = interpret(data)
        print(f"HR: {data['hr']}")
        outlet_hr.push_sample([data['hr']])
        if "rr" in data.keys():
            for data_rr in data["rr"]:
                print(f"    RR: {data_rr}")
                outlet_rr.push_sample([data_rr])
        return data
    else:
        return None


async def main(address):
    client = BleakClient(address)
    try:
        await client.connect()
        print(f"Device Address: {client.address}")
        hr_data = await client.start_notify(HR_UUID, callback)
        while True:
            await asyncio.sleep(0.1)
    except KeyboardInterrupt:
        print(f"Stopped by user")
        await client.stop_notify(HR_UUID)
    except Exception as e:
        print(f"Exeption: {e}")
    finally:
        await client.disconnect()

asyncio.run(main(address))