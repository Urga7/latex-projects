import subprocess
import argparse
import re
import statistics
import time
import signal
import sys

# Store subprocess references so we can clean them up later
stress_processes = []

def launch_stress_l2pings(mac, stress_level):
    for i in range(stress_level):
        cmd = ['sudo', 'l2ping', '-f', mac]
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        stress_processes.append(proc)
    print(f"Started {stress_level} stress processes (l2ping -f)")

def cleanup_stress_processes():
    print("Cleaning up stress processes...")
    for proc in stress_processes:
        proc.terminate()
    for proc in stress_processes:
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

def signal_handler(sig, frame):
    cleanup_stress_processes()
    sys.exit(0)

def run_l2ping(mac, count, delay, stress_level):
    if delay > 0:
        print(f"Waiting {delay} seconds before starting the test...")
        time.sleep(delay)

    # Setup stress
    if stress_level > 0:
        launch_stress_l2pings(mac, stress_level)
        time.sleep(1)  # Give stress processes a moment to start

    # Main l2ping process
    cmd = ['sudo', 'l2ping','-c', str(count), '-f', mac]
    print(f"Pinging {mac} with {count} pings...\n")
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    latencies = []
    output_lines = []

    for line in process.stdout:
        output_lines.append(line)

        match = re.search(r'time (\d+\.\d+)ms', line)
        if match:
            latencies.append(float(match.group(1)))

    process.wait()

    cleanup_stress_processes()

    if process.returncode != 0:
        print(f"l2ping failed with return code {process.returncode}")
        return

    if latencies:
        avg_latency = statistics.mean(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        stddev = statistics.stdev(latencies) if len(latencies) > 1 else 0

        print(f"\n=== Results ===")
        print(f"Average latency: {avg_latency:.2f} ms")
        print(f"Min: {min_latency:.2f} ms, Max: {max_latency:.2f} ms, Stddev: {stddev:.2f} ms")
    else:
        print("No valid latency responses received.")

    # Join all lines and parse for packet loss
    full_output = ''.join(output_lines)
    match = re.search(r'(\d+) sent, (\d+) received, (\d+)% loss', full_output)
    if match:
        sent, received, loss = match.groups()
        print(f"{sent} sent, {received} received, {loss}% loss")


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)  # Handle Ctrl+C cleanly

    parser = argparse.ArgumentParser(description='Bluetooth latency measurement using l2ping.')
    parser.add_argument('mac', help='Bluetooth MAC address')
    parser.add_argument('-c', '--count', type=int, default=10, help='Number of pings')
    parser.add_argument('-d', '--delay', type=int, default=0, help='Delay before starting the test (in seconds)')
    parser.add_argument('-s', '--stress', type=int, default=0, help='Stress level (number of flood l2pings)')

    args = parser.parse_args()
    run_l2ping(args.mac, args.count, args.delay, args.stress)
