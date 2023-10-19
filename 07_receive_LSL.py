"""Example program to demonstrate how to read string-valued markers from LSL."""

from pylsl import StreamInlet, resolve_stream


def main():
    # first resolve a marker stream on the lab network
    print("looking for a marker stream...")
    # streams = resolve_stream('type', 'Markers')
    streams = resolve_stream('name', 'RR')

    # create a new inlet to read from the stream
    inlet = StreamInlet(streams[0])

    try:
        while True:
            # get a new sample (you can also omit the timestamp part if you're not
            # interested in it)
            sample, timestamp = inlet.pull_sample()
            print(f"got {sample[0]} at time {timestamp}")
    except KeyboardInterrupt:
        print("Stopped by user")
    finally:
        print("Disconnecting")
        inlet.close_stream()


if __name__ == '__main__':
    main()