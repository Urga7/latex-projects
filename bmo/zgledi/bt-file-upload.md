### Prenos datoteke preko `obexftp`

Demonstracija uporabe orodja `obexftp` za prenos datoteke na napravo preko Bluetooth povezave. V določenih primerih lahko to predstavlja varnostno tveganje, zlasti če naprava samodejno sprejema datoteke.

#### 1. Iskanje Bluetooth naprav v bližini

Najprej poiščemo naprave v dosegu Bluetooth povezave:

```bash
$ hcitool scan
Scanning ...
        41:42:7B:CB:AC:9E       SBL TW6 C2
        44:EA:30:60:EA:58       Galaxy Buds Pro (EA58)
        F0:CD:31:60:0F:D5       Urban S22
        90:7A:58:E9:9A:BB       WH-XB910N
```

#### 2. Shranjevanje MAC naslova ciljne naprave

Za lažje delo shranimo MAC naslov izbrane naprave v spremenljivko:

```bash
$ PHONE_MAC=F0:CD:31:60:0F:D5
```

#### 3. Pridobitev informacij o storitvah z `sdptool`

Z ukazom `sdptool browse` pregledamo, katere storitve so na voljo na napravi in na katerih kanalih:

```bash
$ sdptool browse $PHONE_MAC
...
Service Name: OBEX Object Push
Service RecHandle: 0x10053
Service Class ID List:
  "OBEX Object Push" (0x1105)
Protocol Descriptor List:
  "L2CAP" (0x0100)
  "RFCOMM" (0x0003)
    Channel: 12
  "OBEX" (0x0008)
...
```

V tem primeru je **OBEX Object Push** storitev dostopna na **kanalu 12**.

#### 4. Prenos datoteke na napravo

Datoteko lahko prenesemo z naslednjim ukazom (zamenjaj `test.txt` z želeno datoteko):

```bash
$ obexftp --noconn --uuid none --bluetooth $PHONE_MAC --channel 12 --put test.txt
Suppressing FBS.
Connecting.. done
Sending "test.txt"... done
Disconnecting.. done
```

> **Opomba:** Na večini modernih naprav bo uporabnik moral **ročno potrditi** prenos.
