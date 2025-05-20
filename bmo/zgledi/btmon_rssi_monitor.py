import subprocess
import re
import datetime
import matplotlib.pyplot as plt
import argparse
import time
import sys
import os

# Ustvarimo parser za argumente ukazne vrstice
parser = argparse.ArgumentParser(description="Zbira Bluetooth RSSI vrednosti z uporabo btmon.")
group = parser.add_mutually_exclusive_group(required=True)

# Določimo število vzorcev ali trajanje zajema kot obvezen argument (eno izmed dveh)
group.add_argument("-n", type=int, help="Število RSSI vzorcev za zajem")
group.add_argument("-t", type=int, help="Trajanje (v sekundah) za zajem RSSI podatkov")

# Opcijsko dodamo zakasnitev pred začetkom zajema
parser.add_argument("-d", type=int, help="Zakasnitev (v sekundah) pred začetkom zbiranja podatkov")
args = parser.parse_args()

# Seznami za shranjevanje RSSI vrednosti in časovnih žigov
rssi_values = []
timestamps = []

# Regularni izraz za iskanje vrstic z RSSI vrednostmi
pattern = re.compile(r'RSSI:\s*(-?\d+)\s*dBm')

try:
    if (args.d):
        print(f"Čakam {args.d} sekund pred začetkom zbiranja podatkov...")
        time.sleep(args.d)
    
    # Zaženemo btmon proces za zajem podatkov
    process = subprocess.Popen(['sudo', '-E', 'btmon'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=0)

    start_time = time.time()

    # Beremo vrstico po vrstico iz izhoda btmon
    for line in iter(process.stdout.readline, b''):
        # Če je čas trajanja presežen, prekinemo z zajemom
        if args.t and (time.time() - start_time) >= args.t:
            break
        
        # Preskočimo vrstice, ki ne vsebujejo "RSSI"
        if b'RSSI' not in line:
            continue

        line = line.decode('utf-8').strip()
        match = pattern.search(line)
        if not match:
            continue

        rssi = int(match.group(1))
        # Preskočimo RSSI = 0, ker predstavlja privzeto vrednost
        if rssi == 0:
            continue

        now = datetime.datetime.now()
        print(f"{now.isoformat()} RSSI: {rssi}")
        rssi_values.append(rssi)
        timestamps.append(now)

        # Če smo zbrali dovolj vzorcev, končamo z zajemom
        if args.n and len(rssi_values) >= args.n:
            break
finally:
    # Prekinemo btmon proces
    process.terminate()

# Predvajamo zvok kot signal za konec
subprocess.run(["pulseaudio", "--start"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
os.system('paplay /usr/share/sounds/freedesktop/stereo/complete.oga')

# Če ni bilo zajetih podatkov, prikažemo sporočilo in zaključimo
if not timestamps:
    print("Ni bilo zajetih RSSI podatkov.")
    sys.exit(1)

# Izračunamo povprečje in izpišemo statistiko
total_readings = len(rssi_values)
average_rssi = sum(rssi_values) / total_readings
print(f"\nSkupno število odčitkov: {total_readings}")
print(f"Povprečna RSSI vrednost: {average_rssi:.2f} dBm")

# Pripravimo podatke za graf (časovni zamik od začetka)
start_time = timestamps[0]
elapsed = [(t - start_time).total_seconds() for t in timestamps]

# Narišemo graf RSSI vrednosti skozi čas
plt.plot(elapsed, rssi_values, marker='o')
plt.xlabel("Čas (s)")
plt.ylabel("RSSI (dBm)")
plt.title("Bluetooth RSSI skozi čas")
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
