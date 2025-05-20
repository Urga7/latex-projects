# Zbiranje Bluetooth RSSI vrednosti z `btmon`

Ta Python program omogoča zbiranje **RSSI** vrednosti (moč signala) iz Bluetooth naprav z uporabo orodja `btmon`, nato pa izriše graf spreminjanja signala skozi čas.

---

## Zahteve za sistem (Kali Linux)

Preden zaženete program, preverite ali imate nameščene naslednje komponente:

### Sistemski paketi

Zaženite naslednji ukaz, da namestite vse potrebne sistemske pakete:

```bash
sudo apt update
sudo apt install -y bluez pulseaudio python3 python3-pip
```

### Python knjižnice

Namestite zahtevane knjižnice:

```bash
pip3 install matplotlib
```

---

## Zagon programa

Skripta omogoča dva načina zajema podatkov:

* Z zbiranjem **določenega števila vzorcev**
* Z zbiranjem podatkov za **določeno trajanje (v sekundah)**

## Načini uporabe

### Z zajemom po številu vzorcev

```bash
sudo python3 rssi_logger.py -n 50
```

Zbira 50 RSSI vrednosti, nato izriše graf.

### Z zajemom po času (npr. 30 sekund)

```bash
sudo python3 rssi_logger.py -t 30
```

Zbira RSSI vrednosti 30 sekund, nato izriše graf.

### Z zakasnitvijo pred začetkom (npr. 10 sekund čakanja, nato 60 sekund zbiranja)

```bash
sudo python3 rssi_logger.py -t 60 -d 10
```

---

## Zvočni signal

Ob koncu programa se predvaja zvočni signal (če `paplay` deluje). V primeru težav preverite ali je `pulseaudio` omogočen:

```bash
pulseaudio --start
```

