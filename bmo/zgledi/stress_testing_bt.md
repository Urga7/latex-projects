
# Bluetooth Latency Tester (l2ping-based)

To orodje omogoča merjenje latence Bluetooth povezave na podlagi ukaza `l2ping`, z možnostjo dodatnega stresnega testa z več hkratnimi `l2ping -f` procesi.

## Zahteve (Kali Linux)

Pred uporabo orodja se prepričaj, da imaš nameščene naslednje komponente:

### Sistemski paketi
```bash
sudo apt update
sudo apt install -y bluez pulseaudio python3 python3-pip
```

### Python knjižnice
Ker skripta uporablja le standardne knjižnice (`argparse`, `re`, `statistics`, `time`, `signal`, `subprocess`, `sys`), **ni treba nameščati dodatnih Python modulov** preko `pip`.

## Uporaba

Zaženite skripto z naslednjimi argumenti:

```bash
sudo python3 bt_latency_test.py <MAC_NASLOV> [možnosti]
```

### Argumenti

| Argument | Opis |
|---------|------|
| `<MAC_NASLOV>` | Bluetooth MAC naslov naprave, ki jo testiramo |
| `-c`, `--count` | Število pingov, privzeto `10` |
| `-d`, `--delay` | Časovni zamik (v sekundah) pred začetkom merjenja |
| `-s`, `--stress` | Število dodatnih stresnih `l2ping -f` procesov za obremenitev povezave |

### Primeri

#### 1. Osnovno merjenje z 10 ping-i:
```bash
sudo python3 bt_latency_test.py AA:BB:CC:DD:EE:FF
```

#### 2. Merjenje z 50 ping-i in 5 sekundnim zamikom:
```bash
sudo python3 bt_latency_test.py AA:BB:CC:DD:EE:FF -c 50 -d 5
```

#### 3. Merjenje z 20 ping-i in stresnim testom z 3 dodatnimi procesi:
```bash
sudo python3 bt_latency_test.py AA:BB:CC:DD:EE:FF -c 20 -s 3
```

## Preklic delovanja

Lahko kadarkoli pritisneš `Ctrl + C`, da se skripta prekine. Vsi dodatni `l2ping -f` procesi se bodo samodejno ustavili.

## Izhod

Skripta izpiše:
- Povprečno, minimalno in maksimalno latenco
- Standardni odklon (če je več meritev)
- Statistiko izgubljenih paketov (število poslanih, prejetih in % izgube)