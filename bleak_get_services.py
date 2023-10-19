import asyncio
from bleak import BleakClient

address = "DB:6E:5B:87:4E:50"
# address = "EF:2C:35:3C:D8:3A"
# address = "0C:8C:DC:24:9A:BF"


def callback(sender: int, data: bytearray):
    print(f"{sender}: {data}")


async def main(address):
    client = BleakClient(address)
    try:
        await client.connect()
        # await client.pair()
        print(f"Device Address: {client.address}")
        print("Device Services: ")
        for s in client.services:
            print(' - service: ', s.handle, s.uuid, s.description)
            chs = s.characteristics
            for c in chs:
                print('  - characteristic: ', c.handle, c.uuid, c.description, c.properties)
                for d in c.descriptors:
                    print("   - descriptors:", d)

        battery_level = await client.read_gatt_char("00002a19-0000-1000-8000-00805f9b34fb")
        print("Battery Level: {0}%".format(int(battery_level[0])), flush=True)
    except Exception as e:
        print(e)
    finally:
        await client.disconnect()

asyncio.run(main(address))