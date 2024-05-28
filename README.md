# Heart Rate Variability

Scripts in order of usage:
 - 01: Simple list ble devices.
   - 01a: Search for a specific ble device.
 - 02: Collect the HR and RR and print them to the screen.
 - 03: Stream the HR and RR data with LSL.
 - 04: Check an XDF file written with the last script.
 - 05: Connect to multiple ble devices, and broadcast for each two streams.
  - 05a: Search for multiple devices.
  - 05b: Connect to multiple devices, no LSL just print.
 - 06: A simple GUI for LSL.
 - 07: Receive and print LSL data.
 - 08: A simple plot from LSL data.
 - 09: Larger visualization of different HRV variables.

TODO:
Compare time deltas.
Compare same subject, multiple devices.
Extract ECG from Polar H10.
Compare RR to HR, ECG to HR, and ECG to RR.


## Breath Rates
| BPM | seconds | inhalation | exhalation | pause |
| --- | --- | --- | --- | --- |
| 10 | 6 | 3 | 3 | 0 |
| 9 | 6.6 | 3.3 | 3.3 | 0 |
| 8 | 7.5 | 3.75 | 3.75 | 0 |
| 7.5 | 8 | 4 | 4 | 0 |
| 6.6 | 9 | 4.5 | 4.5 | 0 |
| 6 | 10 | 5 | 5 | 0 |
| 5.45 | 11 | 5 | 5 | 1 |
| 5 | 12 | 6 | 6 | 0 |
| 4.29 | 14 | 7 | 7 | 0 |
| 4 | 15 | 7 | 7 | 1 |
| 3.7 | 16 | 8 | 8 | 0 |
| 3.33 | 18 | 9 | 9 | 0 |
| 3 | 20 | 10 | 10 | 12 |
| --- | --- | --- | --- | --- |
| 2.5 | 24 | 10 | 10 | 4 |
| 2.22 | 27 | 10 | 12 | 5 |
| 2 | 30 | 10 | 12 | 7 |
| 1.8 | 33 | 12 | 14 | 7 |
| 1.57 | 38 | 15 | 15 | 8 |
| 1.5 | 40 | 15 | 15 | 9 |
| 1.33 | 45 | 15 | 15 | 15 |