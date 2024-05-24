import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import seaborn as sns
import argparse

def create_breathing_gif(bpm, grow_time, shrink_time, color, filename, fps):
    total_time = 60 / bpm  # Total duration of one breath cycle in seconds
    interval = 1000 / fps  # Interval between frames in milliseconds

    # Calculate the number of frames for grow and shrink phases
    frames_grow = int((grow_time / total_time) * (fps * total_time))
    frames_shrink = int((shrink_time / total_time) * (fps * total_time))
    assert frames_grow + frames_shrink > 0, "The total time is too short for the given BPM."

    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(10,10))
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect('equal')
    ax.axis('off')
    
    circle, = ax.plot([], [], color=color, lw=2)

    def init():
        circle.set_data([], [])
        return circle,

    def animate(i):
        # Coral and Teal are the colors in the diverging_palette
        diverging_palette = sns.diverging_palette(180, 16, as_cmap=True)
        if i < frames_grow:
            radius = i / frames_grow
            shrinking = True
        else:
            radius = 1 - (i - frames_grow) / frames_shrink
            shrinking = False

        color = "coral" if shrinking else "teal"
        theta = np.linspace(0, 2 * np.pi, 100)
        x = radius * np.cos(theta)
        y = radius * np.sin(theta)
        circle.set_data(x, y)
        circle.set_linewidth(4 + (3*radius))
        circle.set_color(color)
        return circle,

    ani = animation.FuncAnimation(
        fig, animate, init_func=init, frames=frames_grow + frames_shrink, interval=interval, blit=True
    )

    # Save the animation as a GIF
    ani.save(filename, writer='imagemagick', fps=fps)

    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create a breathing circle GIF.')
    parser.add_argument('--bpm', type=int, default=5, help='Breaths per minute.')
    parser.add_argument('--grow_time', type=float, default=6, help='Time in seconds to grow the circle.')
    parser.add_argument('--shrink_time', type=float, default=6, help='Time in seconds to shrink the circle.')
    parser.add_argument('--color', type=str, default='teal', help='Color of the circle.')
    parser.add_argument('--filename', type=str, default='5.gif', help='Filename of the output GIF.')
    parser.add_argument('--fps', type=int, default=30, help='Frames per second of the GIF.')

    args = parser.parse_args()
    print(args)
    create_breathing_gif(args.bpm, args.grow_time, args.shrink_time, args.color, args.filename, args.fps)
    print(f"Breathing circle GIF saved to {args.filename}")