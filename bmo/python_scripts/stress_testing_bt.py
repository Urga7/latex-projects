import subprocess
import argparse
import re
import statistics
import time
import signal
import sys
import matplotlib.pyplot as plt

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
    stress_processes.clear()


def signal_handler(sig, frame):
    cleanup_stress_processes()
    sys.exit(0)


def single_latency_test(mac, count, stress_level):
    if stress_level > 0:
        launch_stress_l2pings(mac, stress_level)
        time.sleep(1)

    cmd = ['sudo', 'l2ping', '-c', str(count), '-f', mac]
    print(f"\nRunning test with {stress_level} stress processes...")
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
        return None

    # Print packet loss
    full_output = ''.join(output_lines)
    match = re.search(r'(\d+) sent, (\d+) received, (\d+)% loss', full_output)
    if match:
        sent, received, loss = match.groups()
        print(f"{sent} sent, {received} received, {loss}% loss")

    if latencies:
        avg_latency = statistics.mean(latencies)
        print(f"Average latency with {stress_level} stress processes: {avg_latency:.2f} ms")
        return avg_latency
    else:
        print(f"No valid latency responses received with {stress_level} stress processes.")
        return None



def run_multiple_tests(mac, count, max_stress, skip=0, step=1):
    results = []
    for stress_level in range(skip, max_stress + 1, step):
        avg = single_latency_test(mac, count, stress_level)
        if avg is not None:
            results.append((stress_level, avg))
        else:
            results.append((stress_level, 0))
    return results


def plot_results(results):
    stress_levels = [x[0] for x in results]
    latencies = [x[1] for x in results]

    plt.figure(figsize=(10, 6))
    plt.plot(stress_levels, latencies, marker='o', linestyle='-', color='blue')
    plt.title("Bluetooth Latency vs Number of Stress Processes")
    plt.xlabel("Number of Stress Processes")
    plt.ylabel("Average Latency (ms)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(description='Bluetooth latency stress test using l2ping.')
    parser.add_argument('mac', help='Bluetooth MAC address')
    parser.add_argument('-c', '--count', type=int, default=30, help='Number of pings per test (default: 30)')
    parser.add_argument('-n', '--numtests', type=int, default=5, help='Maximum number of stress processes (0 to N)')
    parser.add_argument('-s', '--skip', type=int, default=0, help='Number of initial stress levels to skip (default: 0)')
    parser.add_argument('-t', '--step', type=int, default=1, help='Step size for increasing stress levels (default: 1)')

    args = parser.parse_args()

    results = run_multiple_tests(args.mac, args.count, args.numtests, args.skip, args.step)
    plot_results(results)
