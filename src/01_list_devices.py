import asyncio
from bleak import BleakScanner

async def main():
    devices = await BleakScanner.discover()
    return devices

devices = asyncio.run(main())
for d in devices:
    print(f"Device {d.name}: {d.address}")
    # if d.metadata and "manufacturer_data" in d.metadata.keys():
    #     for key in d.metadata['manufacturer_data']:
    #         print(f"    ManufacturerData: {int(d.metadata['manufacturer_data'][key].hex(), 16)}")