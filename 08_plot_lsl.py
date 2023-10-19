from collections import deque
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from pylsl import StreamInlet, resolve_stream

# Set the number of data points to display in the scrolling plot
MAX_DATA_POINTS = 100

# Initialize an empty deque with zeros
data_buffer = deque([0] * MAX_DATA_POINTS, maxlen=MAX_DATA_POINTS)
last_rr = 0

# Define the animation function to update the plot
def animate(frame):
    global data_buffer, last_rr
    # Get a new sample from the LSL inlet
    sample, timestamp = inlet.pull_sample()
    this_rr = sample[0]
    this_nn = this_rr - last_rr
    print(f"got {this_rr} at time {timestamp}")

    # Append the new data to the deque
    data_buffer.append(this_rr)

    # Update the plot data
    line.set_ydata(data_buffer)
    line.set_xdata(range(len(data_buffer)))

    # Adjust the plot limits to display the scrolling effect
    ax.relim()
    ax.autoscale_view()
    last_rr = this_rr

    return line,

# Create an empty plot
fig, ax = plt.subplots()
line, = ax.plot([])

# Resolve the LSL stream
print("Looking for a marker stream...")
streams = resolve_stream('name', 'RR')
inlet = StreamInlet(streams[0])

# Set up the plot
ax.set_xlim(0, MAX_DATA_POINTS)
# ax.set_ylim(-1, 1)  # Adjust the Y-axis limits as needed
ax.set_title("RR intervals")

ani = FuncAnimation(fig, animate, interval=10)  # Update the plot every 10 milliseconds

try:
    plt.show()
except KeyboardInterrupt:
    print("Stopped by user")
finally:
    print("Disconnecting")
    inlet.close_stream()

