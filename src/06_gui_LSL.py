import asyncio
from tkinter import Tk, Listbox, Button, Label
from bleak import BleakScanner, BleakClient

class BLEBrowser:
    def __init__(self):
        self.root = Tk()
        self.root.title("BLE Browser")

        # Create a Listbox to display discovered BLE devices
        self.listbox = Listbox(self.root)
        self.listbox.pack()

        # Create a "Scan" button to initiate device scanning
        self.scan_button = Button(self.root, text="Scan", command=self.start_scan)
        self.scan_button.pack()

        # Create a "Connect" button to connect to a selected device
        self.connect_button = Button(self.root, text="Connect", state="disabled", command=self.connect_to_device)
        self.connect_button.pack()

        # Create a label to display information about the selected device
        self.selected_device_label = Label(self.root, text="Press 'Scan' to continue...")
        self.selected_device_label.pack()

        # Initialize variables to store discovered devices and the selected device
        self.devices = []
        self.selected_device = None

    async def scan_devices(self):
        # Use BleakScanner to discover nearby BLE devices
        scanner = BleakScanner()
        self.devices = await scanner.discover()

        # Clear the Listbox and display discovered devices
        self.listbox.delete(0, "end")
        for device in self.devices:
            self.listbox.insert("end", device.name)

        # Update the status label
        self.selected_device_label.config(text="Select device")

    def interpret(self, data):
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

    def start_scan(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.scan_devices())

    def on_listbox_select(self, event):
        selected_index = self.listbox.curselection()
        if selected_index:
            # Set the selected device based on the Listbox selection
            self.selected_device = self.devices[selected_index[0]]
            selected_device_name = self.listbox.get(selected_index[0])
            self.selected_device_label.config(text=f"Device: {selected_device_name}")
            self.connect_button.config(state="active")  # Enable the "Connect" button

    async def connect_to_device(self):
        if self.selected_device:
            # Get the device address from the selected device
            address = self.selected_device.address

            # Create a BleakClient for the selected device and start the connection
            async with BleakClient(address) as client:
                await self.manage_client(client)

    async def manage_client(self, client):
        # Handle the BLE client connection and operations
        # (You can add your specific logic here, such as streaming data)
        pass  # Modify this to handle your BLE operations

    def run(self):
        self.root.mainloop()

# Create an instance of the BLEBrowser and run the GUI
ble_browser = BLEBrowser()
ble_browser.run()
