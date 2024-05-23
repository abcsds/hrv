import asyncio
import contextlib
import logging
from typing import Iterable

from bleak import BleakScanner, BleakClient


async def connect_to_device(
    lock: asyncio.Lock,
    address: str,
    notify_uuid: str,
):
    logging.info("starting %s task", address)

    try:
        async with contextlib.AsyncExitStack() as stack:
            # Trying to establish a connection to two devices at the same time
            # can cause errors, so use a lock to avoid this.
            async with lock:
                logging.info("scanning for %s", address)

                device = await BleakScanner.find_device_by_name(address)

                logging.info("stopped scanning for %s", address)

                if device is None:
                    logging.error("%s not found", address)
                    return

                client = BleakClient(device)

                logging.info("connecting to %s", address)

                await stack.enter_async_context(client)

                logging.info("connected to %s", address)

                # This will be called immediately before client.__aexit__ when
                # the stack context manager exits.
                stack.callback(logging.info, "disconnecting from %s", address)

            # The lock is released here. The device is still connected and the
            # Bluetooth adapter is now free to scan and connect another device
            # without disconnecting this one.

            def callback(_, data):
                logging.info("%s received %r", address, data)

            await client.start_notify(notify_uuid, callback)
            await asyncio.sleep(10.0)
            await client.stop_notify(notify_uuid)

        # The stack context manager exits here, triggering disconnection.

        logging.info("disconnected from %s", address)

    except Exception:
        logging.exception("error with %s", address)


async def main(
    addresses: Iterable[str],
    uuids: Iterable[str],
):
    lock = asyncio.Lock()

    await asyncio.gather(
        *(
            connect_to_device(lock, address, uuid)
            for address, uuid in zip(addresses, uuids)
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
    uuids = [d["uuid"] for d in devices]
    debug = False
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    )

    asyncio.run(
        main(
            addresses,
            uuids,
        )
    )