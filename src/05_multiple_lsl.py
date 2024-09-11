import asyncio
import contextlib
import logging
from typing import Iterable

from bleak import BleakScanner, BleakClient
from pylsl import StreamInfo, StreamOutlet
from helperfuncs import interpret

async def connect_to_device(
    lock: asyncio.Lock,
    device: dict,
    address: str,
    outlet_rr: StreamOutlet,
):
    logging.info("starting %s task", address)

    try:
        async with contextlib.AsyncExitStack() as stack:
            # Trying to establish a connection to two devices at the same time
            # can cause errors, so use a lock to avoid this.
            async with lock:
                logging.info("scanning for %s", address)

                found_device = await BleakScanner.find_device_by_address(address, timeout=30.0, scanning_mode="active")

                logging.info("stopped scanning for %s", address)

                if found_device is None:
                    logging.error("%s not found", address)
                    return

                client = BleakClient(found_device)

                logging.info("connecting to %s", address)

                await stack.enter_async_context(client)

                logging.info("connected to %s", address)

                # This will be called immediately before client.__aexit__ when
                # the stack context manager exits.
                stack.callback(logging.info, "disconnecting from %s", address)

            # The lock is released here. The device is still connected and the
            # Bluetooth adapter is now free to scan and connect another device
            # without disconnecting this one.

            # def callback(_, data):
            #     logging.info("%s received %r", address, data)

            def callback(sender: int, data: bytearray):
                if data:
                    data = interpret(data)
                    logging.info(f"{device['name']} HR: {data['hr']}")
                    if "rr" in data.keys():
                        for data_rr in data["rr"]:
                            logging.info(f"                   RR: {data_rr}")
                            outlet_rr.push_sample([data_rr])
                    return data
                else:
                    return None

            hr_data = await client.start_notify(device["uuid"], callback)
            logging.info("HR data received from %s", address)
            while True:
                await asyncio.sleep(0.01)

        # The stack context manager exits here, triggering disconnection.
        # await client.stop_notify(HR_UUID)
        logging.info("disconnected from %s", address)

    except Exception:
        logging.exception("error with %s", address)


async def main(devices: dict, addresses: Iterable[str]):
    device_names = [d["name"] for d in devices]
    infos_hr = [
        StreamInfo(name=f'HR_{device_name}',
            type='Markers',
            channel_count=1,
            channel_format='int32',
            source_id=f'HR_{device_name}_markers')
        for device_name in device_names
    ]
    infos_rr = [
        StreamInfo(name=f'RR_{device_name}',
            type='Markers',
            channel_count=1,
            channel_format='int32',
            source_id=f'RR_{device_name}_markers')
        for device_name in device_names
    ]
    outlets_rr = [StreamOutlet(info_rr) for info_rr in infos_rr]
    lock = asyncio.Lock()
    await asyncio.gather(
        *(
            connect_to_device(lock, device, address, outlet_rr)
            for device, address, outlet_rr in zip(devices, addresses, outlets_rr)
        )
    )


if __name__ == "__main__":
    devices = [
        # {"address": "C8:28:E6:77:9D:0D", "name": "Polar H10 D6B5C724", "uuid": "00002a37-0000-1000-8000-00805f9b34fb"},
        # {"address": "D6:E7:A7:D1:29:AE", "name": "Polar H10 CA549123", "uuid": "00002a37-0000-1000-8000-00805f9b34fb"},
        # LaSalle
        {"address": "DB:10:0A:6B:80:E8", "name": "Polar H10 D66F812D", "uuid": "00002a37-0000-1000-8000-00805f9b34fb"}, # 1
        {"address": "D8:40:B0:01:39:EF", "name": "Polar H10 D66F7F28", "uuid": "00002a37-0000-1000-8000-00805f9b34fb"}, # 2
    ]
    addresses = [d["address"] for d in devices]
    debug = False
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    )

    asyncio.run(main(devices, addresses))