import subprocess
import re
import datetime
import matplotlib.pyplot as plt
import argparse
import time
import sys
import os

# --- Argument Parsing ---
parser = argparse.ArgumentParser(description="Collect Bluetooth RSSI values using btmon.")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-n", type=int, help="Number of RSSI samples to collect")
group.add_argument("-t", type=int, help="Duration in seconds to collect RSSI data")

parser.add_argument("-d", type=int, help="Delay in seconds before starting data collection")  # Not mutually exclusive
args = parser.parse_args()


# --- RSSI Data Containers ---
rssi_values = []
timestamps = []

pattern = re.compile(r'RSSI:\s*(-?\d+)\s*dBm')

try:
    if (args.d):
        print(f"Waiting for {args.d} seconds before starting to collect data...")
        time.sleep(args.d)
          

    # --- Start btmon subprocess ---
    process = subprocess.Popen(['sudo', '-E', 'btmon'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=0)

    start_time = time.time()

    for line in iter(process.stdout.readline, b''):
        if args.t and (time.time() - start_time) >= args.t:
            break
        
        if b'RSSI' not in line:
            continue

        line = line.decode('utf-8').strip()
        match = pattern.search(line)
        if not match:
            continue

        rssi = int(match.group(1))
        if rssi == 0:
            continue

        now = datetime.datetime.now()
        print(f"{now.isoformat()} RSSI: {rssi}")
        rssi_values.append(rssi)
        timestamps.append(now)

        if args.n and len(rssi_values) >= args.n:
            break
finally:
    process.terminate()


# --- Play Sound Notification ---
subprocess.run(["pulseaudio", "--start"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
os.system('paplay /usr/share/sounds/freedesktop/stereo/complete.oga')

if not timestamps:
    print("No RSSI data collected.")
    sys.exit(1)
    
# --- Summary ---
total_readings = len(rssi_values)
average_rssi = sum(rssi_values) / total_readings
print(f"\nTotal readings collected: {total_readings}")
print(f"Average RSSI value: {average_rssi:.2f} dBm")

# --- Plotting ---
start_time = timestamps[0]
elapsed = [(t - start_time).total_seconds() for t in timestamps]
plt.plot(elapsed, rssi_values, marker='o')
plt.xlabel("Time (s)")
plt.ylabel("RSSI (dBm)")
plt.title("Bluetooth RSSI Over Time")
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
