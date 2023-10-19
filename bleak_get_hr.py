import asyncio
from bleak import BleakClient
from pylsl import StreamInfo, StreamOutlet


# address = "EF:2C:35:3C:D8:3A"
# address = "DB:6E:5B:87:4E:50" # Polar H10
address = "DE:C5:AC:14:25:28" # HR6 0039090
HR_UUID = "00002a37-0000-1000-8000-00805f9b34fb"

# address = "0C:8C:DC:24:9A:BF"
# HR_UUID = "00002a37-0000-1000-8000-00805f9b34fb"
info_hr = StreamInfo(name='HR',
    type='Markers',
    channel_count=1,
    channel_format='int32',
    source_id='HR_markers_ID42'
)
info_rr = StreamInfo(name='RR',
    type='Markers',
    channel_count=1,
    channel_format='string',
    source_id='RR_markers_ID42'
)
outlet_hr = StreamOutlet(info_hr)
outlet_rr = StreamOutlet(info_rr)


def interpret(data):
    """
    from fg1/BLEHeartRateLogger
    data is a list of integers corresponding to readings from the BLE HR monitor
    """
    byte0 = data[0]
    res = {}
    res["hrv_uint8"] = (byte0 & 1) == 0
    sensor_contact = (byte0 >> 1) & 3
    if sensor_contact == 2:
        res["sensor_contact"] = "No contact detected"
    elif sensor_contact == 3:
        res["sensor_contact"] = "Contact detected"
    else:
        res["sensor_contact"] = "Sensor contact not supported"

    res["ee_status"] = ((byte0 >> 3) & 1) == 1
    res["rr_interval"] = ((byte0 >> 4) & 1) == 1
    if res["hrv_uint8"]:
        res["hr"] = data[1]
        i = 2
    else:
        res["hr"] = (data[2] << 8) | data[1]
        i = 3
    if res["ee_status"]:
        res["ee"] = (data[i + 1] << 8) | data[i]
        i += 2
    if res["rr_interval"]:
        res["rr"] = []
        while i < len(data):
            # Note: Need to divide the value by 1024 to get in seconds
            res["rr"].append((data[i + 1] << 8) | data[i])
            i += 2
    return res

def callback(sender: int, data: bytearray):
    if data:
        data = interpret(data)
        print(f"HR: {data['hr']}, RR: {data['rr']}")
        outlet_hr.push_sample([data["hr"]])
        outlet_rr.push_sample([f"{data['rr']}"])
        return data
    else:
        return None


async def main(address):
    client = BleakClient(address)
    try:
        await client.connect()
        print(f"Device Address: {client.address}")
        hr = await client.start_notify(HR_UUID, callback)
        await asyncio.sleep(30)
        await client.stop_notify(HR_UUID)
    except Exception as e:
        print(f"Exeption: {e}")
    finally:
        await client.disconnect()

asyncio.run(main(address))