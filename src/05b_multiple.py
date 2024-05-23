import asyncio
import contextlib
import logging
from typing import Iterable

from bleak import BleakScanner, BleakClient
from helperfuncs import interpret

HR_UUID = "00002a37-0000-1000-8000-00805f9b34fb"

async def connect_to_device(
    lock: asyncio.Lock,
    device: dict,
    address: str,
):
    logging.info("starting %s task", address)

    try:
        async with contextlib.AsyncExitStack() as stack:
            # Trying to establish a connection to two devices at the same time
            # can cause errors, so use a lock to avoid this.
            async with lock:
                logging.info("scanning for %s", address)

                found_device = await BleakScanner.find_device_by_address(address, timeout=20.0, scanning_mode="active")

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
                    # outlet_hr.push_sample([data['hr']])
                    if "rr" in data.keys():
                        for data_rr in data["rr"]:
                            logging.info(f"    {device['name']} RR: {data_rr}")
                            # outlet_rr.push_sample([data_rr])
                    return data
                else:
                    return None

            hr_data = await client.start_notify(HR_UUID, callback)
            while True:
                await asyncio.sleep(0.1)

        # The stack context manager exits here, triggering disconnection.
        # await client.stop_notify(HR_UUID)
        logging.info("disconnected from %s", address)

    except Exception:
        logging.exception("error with %s", address)


async def main(devices: dict, addresses: Iterable[str]):
    lock = asyncio.Lock()
    await asyncio.gather(
        *(
            connect_to_device(lock, device, address)
            for device, address in zip(devices, addresses)
        )
    )


if __name__ == "__main__":
    devices = [
        {"address": "DB:6E:5B:87:4E:50", "name": "Polar H10", "uuid": "00002a37-0000-1000-8000-00805f9b34fb"},
        {"address": "DE:C5:AC:14:25:28", "name": "HR6 0039090", "uuid": "00002a37-0000-1000-8000-00805f9b34fb"},
        # {"address": "CD:4B:39:D5:62:36", "name": "HR-70ECAB5D", "uuid": "00002a37-0000-1000-8000-00805f9b34fb"},
        # {"address": "CB:1E:40:C8:F6:03", "name": "HR-70EC985D", "uuid": "00002a37-0000-1000-8000-00805f9b34fb"},
        # {"address": "DB:D1:1C:A1:57:3D", "name": "HR-70EC845D", "uuid": "00002a37-0000-1000-8000-00805f9b34fb"},
        # {"address": "FF:D2:0F:F3:FE:EC", "name": "HR-70ECE75D", "uuid": "00002a37-0000-1000-8000-00805f9b34fb"},
        # {"address": "E8:9B:59:E2:8C:71", "name": "HR-70ECD35D", "uuid": "00002a37-0000-1000-8000-00805f9b34fb"},
        # {"address": "F2:48:B2:FF:3E:CE", "name": "HR-70ECD05D", "uuid": "00002a37-0000-1000-8000-00805f9b34fb"},
    ]
    addresses = [d["address"] for d in devices]
    debug = False
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    )

    asyncio.run(main(devices, addresses))