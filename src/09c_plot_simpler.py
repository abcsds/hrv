from collections import deque
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from pylsl import StreamInlet, resolve_stream
import numpy as np
from scipy import signal
from matplotlib.patches import Rectangle
import tkinter as tk

# Set the number of data points to display in the scrolling plot
MAX_DATA_POINTS = 100
SDNN_WINDOW_SIZE = 100 # Number of points taken into account for the std

average_hr = 60  # Average human hr
average_rr = 1000 * average_hr / 60  # Average human rr in ms
initial_timestamp = None
hb = 0  # Heart beat counter

# Initialize an empty deque with zeros
timestamps = deque([np.nan] * MAX_DATA_POINTS, maxlen=MAX_DATA_POINTS)
hr_data_buffer = deque([average_hr] * MAX_DATA_POINTS, maxlen=MAX_DATA_POINTS)
rr_data_buffer = deque([average_rr] * MAX_DATA_POINTS, maxlen=MAX_DATA_POINTS)
nn_data_buffer = deque([0] * MAX_DATA_POINTS, maxlen=MAX_DATA_POINTS)
sdnn_data_buffer = deque([0] * MAX_DATA_POINTS, maxlen=MAX_DATA_POINTS)
rmssd_data_buffer = deque([0] * MAX_DATA_POINTS, maxlen=MAX_DATA_POINTS)
last_rr = average_rr


# Prompt the user for device
# Define the addresses, names, and UUIDs of devices
devices = [
    # {"address": "DB:6E:5B:87:4E:50", "name": "Polar H10", "uuid": "00002a37-0000-1000-8000-00805f9b34fb"},
    {"address": "C8:28:E6:77:9D:0D", "name": "Polar H10 D6B5C724", "uuid": "00002a37-0000-1000-8000-00805f9b34fb"},
    # {"address": "A0:9E:1A:C5:36:32", "name": "Polar Sense C5363229", "uuid": "00002a37-0000-1000-8000-00805f9b34fb"},
    {"address": "D6:E7:A7:D1:29:AE", "name": "Polar H10 CA549123", "uuid": "00002a37-0000-1000-8000-00805f9b34fb"},
    {"address": "DE:C5:AC:14:25:28", "name": "HR6 0039090", "uuid": "00002a37-0000-1000-8000-00805f9b34fb"},
    {"address": "CD:4B:39:D5:62:36", "name": "HR-70ECAB5D", "uuid": "00002a37-0000-1000-8000-00805f9b34fb"},
    {"address": "CB:1E:40:C8:F6:03", "name": "HR-70EC985D", "uuid": "00002a37-0000-1000-8000-00805f9b34fb"},
    {"address": "DB:D1:1C:A1:57:3D", "name": "HR-70EC845D", "uuid": "00002a37-0000-1000-8000-00805f9b34fb"},
    {"address": "FF:D2:0F:F3:FE:EC", "name": "HR-70ECE75D", "uuid": "00002a37-0000-1000-8000-00805f9b34fb"},
    {"address": "E8:9B:59:E2:8C:71", "name": "HR-70ECD35D", "uuid": "00002a37-0000-1000-8000-00805f9b34fb"},
    {"address": "F2:48:B2:FF:3E:CE", "name": "HR-70ECD05D", "uuid": "00002a37-0000-1000-8000-00805f9b34fb"},
]
selected_device = None
device_names = [device["name"] for device in devices]
root = tk.Tk()

# Create a Listbox widget and populate it with the names
listbox = tk.Listbox(root)
for name in device_names:
    listbox.insert(tk.END, name)

# Create a status bar label
status_var = tk.StringVar()
status_label = tk.Label(root, textvariable=status_var)
status_var.set("Select a device")

# Create a function to handle the user's selection
def on_select(event):
    global selected_device
    selected_index = listbox.curselection()
    if selected_index:
        selected_device = devices[selected_index[0]]
        status_var.set(f"Selected device: {selected_device['name']}")
        root.destroy()
    else:
        status_var.set("Select a device")
        print("No device selected.")

# Create a button to trigger the selection
select_button = tk.Button(root, text="Select", command=on_select)

# Bind the Listbox selection to the on_select function
listbox.bind("<<ListboxSelect>>", on_select)

# Pack the Listbox, status bar, and button
listbox.pack()
status_label.pack()
select_button.pack()

# Start the tkinter main loop
root.mainloop()

# Define the animation function to update the plot
def animate(frame):
    global hr_data_buffer, rr_data_buffer, nn_data_buffer, sdnn_data_buffer, rmssd_data_buffer, last_rr, initial_timestamp, hb

    # Get a new sample from the LSL inlet
    sample, timestamp = inlet.pull_sample()
    if initial_timestamp is None:
        initial_timestamp = timestamp
        timestamps.append(0)
    else:
        timestamps.append(timestamps[-1] + sample[0] / 1000)
    hb += 1
    # timestamps.append(timestamp - initial_timestamp)
    this_rr = sample[0]  # RR peaks in ms
    this_nn = this_rr - last_rr  # differential of RR peaks in ms
    hr = 60 / (this_rr / 1000)  # Heart Rate (HR) peaks in bpm
    this_sdnn = np.std([rr_data_buffer[-i] for i in range(1, SDNN_WINDOW_SIZE)])
    this_rmssd = np.std([nn_data_buffer[-i] for i in range(1, SDNN_WINDOW_SIZE)])
    # Extract fs from all the timestamps
    fs = 1 / np.median(np.diff(timestamps))
    if np.isnan(fs):
        fs = 1.0

    # Extract the frequency spectrum of the RR intervals
    # freq, power = signal.periodogram(rr_data_buffer, fs=fs, window="hann", scaling="density")
    # Use lomb-scargle instead of periodogram
    # freq = np.linspace(0.001, 0.4, 100)
    # signal is in ms, so freq is ms^-1
    freq = np.linspace(0.001, 0.4, MAX_DATA_POINTS)
    # t = np.array(timestamps)
    # t = range(len(rr_data_buffer))
    t = (np.array(timestamps)- timestamps[0])[:len(rr_data_buffer)]
    power = signal.lombscargle(t, rr_data_buffer, freq * 2 * np.pi)

    # Extract power for the frequency bands
    # HF: from 0.15 to 0.4 Hz
    # LF: from 0.04 to 0.15 Hz
    # VLF: from 0.0033 to 0.04 Hz
    hf_power = np.sum(power[(freq >= 0.15) & (freq <= 0.4)])
    lf_power = np.sum(power[(freq >= 0.04) & (freq <= 0.15)])
    vlf_power = np.sum(power[(freq >= 0.0033) & (freq <= 0.04)])

    # Append the new data to the deques
    hr_data_buffer.append(hr)
    rr_data_buffer.append(this_rr)
    nn_data_buffer.append(this_nn)
    sdnn_data_buffer.append(this_sdnn)
    rmssd_data_buffer.append(this_rmssd)

    # RMS of the RR intervals
    rms = np.sqrt(np.mean(np.square(nn_data_buffer)))

    # Update the plot data
    line_hr.set_ydata(hr_data_buffer)
    line_hr.set_xdata(timestamps)

    # line_rr.set_ydata(rr_data_buffer)
    # line_rr.set_xdata(timestamps)

    line_nn.set_ydata(np.multiply(nn_data_buffer, -1))
    line_nn.set_xdata(timestamps)

    line_sdnn.set_ydata(sdnn_data_buffer)
    line_sdnn.set_xdata(timestamps)
    
    line_rmmsd.set_ydata(rmssd_data_buffer)
    line_rmmsd.set_xdata(timestamps)

    # Normalize power before plotting
    n_power = power / np.sum(power)
    # freq_plot.set_ydata(n_power)
    # freq_plot.set_xdata(freq)

    # Update titles
    min_hr = np.min(hr_data_buffer)
    max_hr = np.max(hr_data_buffer)
    str_rng = hb > len(hr_data_buffer) and f"RNG {min_hr:.2f} - {max_hr:.2f} BPM" or ""
    ax_hr.set_title(f"HR (AVG {np.mean(hr_data_buffer):.2f} BPM, LST {hr:.2f} BPM), {str_rng} , fs={fs:.4f}")
    # ax_rr.set_title(f"RR Intervals (AVG {np.mean(rr_data_buffer):.2f} ms, LST {this_rr:.2f} ms)")
    ax_sdnn.set_title(f"SDNN over last {SDNN_WINDOW_SIZE} RR intervals (SDNN {this_sdnn:.2f} ms, RMSSD {this_rmssd:.2f} ms)")

    # Fill the positive values of nn_data_buffer with green and the negative in red
    ax_nn.fill_between(timestamps, 0, np.multiply(nn_data_buffer, -1), where=np.array(np.multiply(nn_data_buffer, -1)) >= 0, facecolor="coral", alpha=0.2)
    ax_nn.fill_between(timestamps, 0, np.multiply(nn_data_buffer, -1), where=np.array(np.multiply(nn_data_buffer, -1)) < 0, facecolor="teal", alpha=0.2)

    # Get score of sympathetic vs parasimpathetic in a range from -1 to 1
    # Do so by averaging the area of the positive and negative parts of the nn_data_buffer
    nn_interpret = np.multiply(nn_data_buffer, -1)
    nn_area_total = np.sum(np.abs(nn_interpret))
    nn_area_pos = np.sum(nn_interpret[nn_interpret >= 0])
    nn_area_neg = np.sum(nn_interpret[nn_interpret < 0])

    nn_ratio_pos = nn_area_pos**2
    nn_ratio_neg = nn_area_neg**2 
    # nn_balance = nn_ratio_pos * 2 - 1
    nn_balance = np.sqrt(nn_ratio_pos - nn_ratio_neg) / nn_area_total

    # Add red markers for the NN peaks above 50 ms
    threshold = np.abs(np.array(nn_data_buffer)) > 50
    pnn50s = -np.array(nn_data_buffer)[threshold]
    pnn50s_t = np.array(timestamps)[threshold]
    ax_nn.scatter(pnn50s_t, pnn50s, c="r")
    pnn50 = len(pnn50s)/len(nn_data_buffer)
    min_nn = np.min(nn_data_buffer)
    max_nn = np.max(nn_data_buffer)
    ax_nn.set_title(f"-ΔRR (Δms), PNN50: {pnn50*100:.2f}%, NN balance: {nn_balance:.2f}, RNG {min_nn:.2f} - {max_nn:.2f} ms")

    # Add markers for the 3 highest frequencies
    top_freqs_idx = np.argsort(power)[-3:]
    top_freqs = freq[top_freqs_idx]
    top_powers = power[top_freqs_idx]
    # ax_freq.scatter(top_freqs, top_powers, c="r", marker="x", s=20)
    # Highest frequency first
    top_freqs = np.flip(top_freqs)
    # Round to 4 decimals
    top_freqs = [np.round(i, 4) for i in top_freqs]
    # Convert to BPM
    top_freqs_bpm = np.multiply(top_freqs, 60)
    top_freqs_bpm = [np.round(i, 2) for i in top_freqs_bpm]
    # str_top_freqs = ", ".join([f"{top_freqs[i]:.4f} Hz ({top_freqs_bpm[i]:.2f} BPM)" for i in range(3)])
    # str_top_freqs = hb >= len(hr_data_buffer) and f", Top 3: {top_freqs_bpm} BPM {top_freqs} Hz" or ""
    # ax_freq.set_title(f"Frequency Spectrum {str_top_freqs}")

    print(f"got {hr} at time {timestamp - initial_timestamp:.4f}s, fs={fs:.4f}, beat {hb}")
    print(f"    PNN50: {pnn50:.4f}, SDNN: {this_sdnn:.4f}, RMS: {rms:.4f}")
    print(f"    HF: {hf_power:.4f}, LF: {lf_power:.4f}, VLF: {vlf_power:.4f}")
    print(f"    Total power: {np.sum(power):.4f}, HF/LF: {hf_power/lf_power:.4f}")
    print(f"    Top 3 frequencies: {top_freqs}, BPM: {top_freqs_bpm}")

    # Add a vertical line to the HR plot
    # ax_nn.hlines(0, timestamps[0], timestamps[-1], colors="k", lw=1, alpha=0.2)

    # Adjust the plot limits to display the scrolling effect
    ax_hr.relim()
    ax_hr.autoscale_view()
    # ax_rr.relim()
    # ax_rr.autoscale_view()
    ax_nn.relim()
    ax_nn.autoscale_view()
    ax_sdnn.relim()
    ax_sdnn.autoscale_view()
    # ax_freq.relim()
    # ax_freq.autoscale_view()

    last_rr = this_rr

    # return line_hr, line_rr, line_nn, line_sdnn,
    # return line_hr, line_rr, line_nn, line_sdnn, freq_plot
    return line_hr, line_nn, line_sdnn, line_rmmsd

# Resolve the LSL stream
print("Looking for a marker stream...")
device_name = selected_device["name"]
streams = resolve_stream('name', f"RR {device_name}")
inlet = StreamInlet(streams[0])

# Create an empty figure and plots
plot_sf = 2.5
fig = plt.figure(figsize=(6.4 * plot_sf, 4.8 * plot_sf), layout="constrained")
fig.canvas.manager.set_window_title(f"{device_name} HRV Live Plot")
gs0 = fig.add_gridspec(3, 2)

ax_hr = fig.add_subplot(gs0[0, :2])
# ax_rr = fig.add_subplot(gs0[0, 0])
ax_nn = fig.add_subplot(gs0[1, :2])
ax_sdnn = fig.add_subplot(gs0[2, :2])

# ax_freq = fig.add_subplot(gs0[2:, 1])

# Create empty plots
# line_hr, = ax_hr.step([],[], where="post", c="tab:blue")
line_hr, = ax_hr.plot([], c="tab:blue")
# line_rr, = ax_rr.plot([], c="tab:orange")
line_nn, = ax_nn.plot([], c="tab:green")
line_sdnn, = ax_sdnn.plot([], c="tab:red")
line_rmmsd, = ax_sdnn.plot([], c="tab:pink")
# freq_plot,= ax_freq.plot([], c="tab:purple")


# Set up the plots
# Show spectrum with a marked window for the bands
# ax_freq.add_patch(Rectangle((0.15, 0), 0.25, 1, alpha=0.2, color="tab:pink", label="HF"))
# ax_freq.add_patch(Rectangle((0.04, 0), 0.11, 1, alpha=0.2, color="tab:olive", label="LF"))
# ax_freq.add_patch(Rectangle((0.0033, 0), 0.0367, 1, alpha=0.2, color="tab:cyan", label="VLF"))
# ax_freq.legend()

# Draw window for SDNS
# ax_rr.add_patch(Rectangle((average_rr, MAX_DATA_POINTS - SDNN_WINDOW_SIZE), SDNN_WINDOW_SIZE, 20, alpha=0.2, color="r", label="SDNN window"))


# Add a vertical line to the HR plot
ax_nn.hlines(0, timestamps[0], timestamps[-1], colors="k", lw=1, alpha=0.2)

# ax_hr.set_xlim(0, MAX_DATA_POINTS)
# ax_rr.set_xlim(0, MAX_DATA_POINTS)
# ax_nn.set_xlim(0, MAX_DATA_POINTS)
# ax_sdnn.set_xlim(0, MAX_DATA_POINTS)

# Titles for each subplot
ax_hr.set_title("Heart Rate (BPM)")
# ax_rr.set_title("RR Intervals (ms)")
ax_nn.set_title("-ΔRR (Δms)")
ax_sdnn.set_title(f"SDNN over last {SDNN_WINDOW_SIZE} RR intervals")
# ax_freq.set_title("Frequency Spectrum")
# ax_freq.set_xlabel("Frequency (Hz)")

ani = FuncAnimation(fig, animate, interval=10)  # Update the plot every 10 milliseconds

try:
    plt.show()
except KeyboardInterrupt:
    print("Stopped by user")
finally:
    print("Disconnecting")
    inlet.close_stream()

