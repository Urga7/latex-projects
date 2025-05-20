
import subprocess
import argparse
import re
import statistics
import time
import signal
import sys

# Seznam procesov za stresni test
stress_processes = []

# Funkcija za zagon več l2ping procesov v načinu flood (stresni test)
def launch_stress_l2pings(mac, stress_level):
    for i in range(stress_level):
        cmd = ['sudo', 'l2ping', '-f', mac]
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        stress_processes.append(proc)
    print(f"Zagnanih {stress_level} stresnih procesov (l2ping -f)")

# Funkcija za čiščenje stresnih procesov
def cleanup_stress_processes():
    print("Ustavljanje stresnih procesov...")
    for proc in stress_processes:
        proc.terminate()
    for proc in stress_processes:
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

# Upravljanje prekinitve (Ctrl+C)
def signal_handler(sig, frame):
    cleanup_stress_processes()
    sys.exit(0)

# Glavna funkcija za izvedbo l2ping in merjenje latenc
def run_l2ping(mac, count, delay, stress_level):
    if delay > 0:
        print(f"Čakanje {delay} sekund pred začetkom testa...")
        time.sleep(delay)

    # Če je določen stresni nivo, zaženemo dodatne flood pinge
    if stress_level > 0:
        launch_stress_l2pings(mac, stress_level)
        time.sleep(1)  # počakamo kratek čas, da se stresni testi vzpostavijo

    # Osnovni ukaz za l2ping z določeno količino pingov
    cmd = ['sudo', 'l2ping','-c', str(count), '-f', mac]
    print(f"Pinganje {mac} z {count} ping-i...\n")
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    latencije = []
    output_lines = []

    # Branje izhoda vrnjenega iz l2ping in shranjevanje latenc
    for line in process.stdout:
        output_lines.append(line)

        match = re.search(r'time (\d+\.\d+)ms', line)
        if match:
            latencije.append(float(match.group(1)))

    process.wait()

    cleanup_stress_processes()

    # Preverimo, ali je ukaz uspel
    if process.returncode != 0:
        print(f"l2ping ni uspel, koda: {process.returncode}")
        return

    # Izračunamo in izpišemo statistiko latenc
    if latencije:
        avg_latency = statistics.mean(latencije)
        min_latency = min(latencije)
        max_latency = max(latencije)
        stddev = statistics.stdev(latencije) if len(latencije) > 1 else 0

        print(f"\n=== Rezultati ===")
        print(f"Povprečna latenca: {avg_latency:.2f} ms")
        print(f"Min: {min_latency:.2f} ms, Max: {max_latency:.2f} ms, Std odklon: {stddev:.2f} ms")
    else:
        print("Ni bilo prejetih veljavnih odgovorov z latenco.")

    # Dodatna statistika o številu poslanih/prejetih paketov in izgubah
    full_output = ''.join(output_lines)
    match = re.search(r'(\d+) sent, (\d+) received, (\d+)% loss', full_output)
    if match:
        sent, received, loss = match.groups()
        print(f"{sent} poslanih, {received} prejetih, {loss}% izgube")


# Glavni vstop v program
if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(description='Merjenje Bluetooth latence z uporabo l2ping.')
    parser.add_argument('mac', help='Bluetooth MAC naslov')
    parser.add_argument('-c', '--count', type=int, default=10, help='Število pingov')
    parser.add_argument('-d', '--delay', type=int, default=0, help='Zakasnitev pred začetkom testa (v sekundah)')
    parser.add_argument('-s', '--stress', type=int, default=0, help='Stresni nivo (število dodatnih flood l2pingov)')

    args = parser.parse_args()
    run_l2ping(args.mac, args.count, args.delay, args.stress)
