HiSPARC VPN
===========

Er zijn twee VPNs:
- een stations VPN. Hierin zitten alle stations. Station kunnen elkaar niet benaderen.
- een admin VPN. In dit VPN loggen beheerders/coordinator in. Vanuit dit VPN kunnen alle stations (die in verbinding gemaakt hebben met het stations VPN) benaderd worden. (VNC e.d.)

OpenVPN configs staan op tietar in `/etc/openvpn`

```
client.conf   # stations VPN
admin.conf    # admin VPN
openssl.conf  # openssl config voor keys
openssladmin.conf # openssl config voor admin adminkeys
client/       # de keys die nodig zijn voor OpenVPN van het stations VPN
admin/        # de keys die nodig zijjn voor OpenVPN van het admin VPN
keys/         # PKI/sleutelparen stations VPN
adminkeys/    # PKI/sleutelparen admin VPN
# de sleutelparen worden via de admin interface van pique
# gemaakt door `hisparcvpnd` (met `easy_rsa`) en in deze
# mappen opgeslagen
easy_rsa     # scripts om met openssl sleutelparen en sigs te maken.
```

OpenVPN logt naar syslog: `/var/log/messages`
OpenVPN herstarten: `sudo service openvpn restart`


De certificaten voor het HiSPARC VPN
====================================

OpenVPN gebruikt x509 certificaten (zoals TLS/SSL voor HTTPS) voor het 
verifieren van de identiteit van servers/clients bij het inloggen.
x509 gebruikt een RSA publiek/geheim sleutelpaar als cryptografische basis.
De x509 PKI is gebaseerd op een vertrouwde centrale service: De root certificate
authority: `root CA`.

Er zijn type drie bestanden:

- `naam.key`: De RSA geheime sleutel. Moet geheim blijven.
- `naam.csr`: `Certificate Signing Request`: De publieke sleutel met contact
info. Waardeloos omdat de echtheid niet kan worden geverifieerd. Een CA
(Certificate Authority) maakt hiervan een certificaat.
- `naam.crt`: Certificaat: RSA publieke sleutel digitaal ondertekend, in ons
geval door de root CA geheime sleutel.

Het admin VPN gebruikt een ander root CA sleutelpaar dan het station VPN. 
De client/server van beide VPNs gebruiken wel dezelfde root CA.
Dat wil zeggen clients en server gebruiken hetzelfde RSA sleutelpaar als root.

De CA root bestanden zijn:
```
ca.crt  # publiek
ca.key  # geheim. Niet op de server bewaren!
```
Het publieke deel (`ca.crt`) bevat de RSA publieke sleutel. Hiermee kunnen
signatures van andere sleutels geverifieerd worden. Dit bestand is op alle
clients nodig.

`ca.key` is in de HiSPARC implementatie op de server nodig, omdat het nodig
is om nieuwe stations certificaten te ondertekenen. `tietar` is ook de CA.

De server heeft een sleutelpaar:
```
server.crt  # publiek: RSA publieke sleutel ondertekend door root CA
server.csr  # niet nodig. Gooi weg.
server.key  # geheim. Moet op server staan.
```

Alle clients (elk station, elke admin) hebben een RSA sleutelpaar:

```
station.crt  # publiek: RSA publieke sleutel ondertekend door root CA
station.csr  # niet nodig. Gooi weg.
station.key  # geheim. Niet op de server bewaren! Is nodig op de client.
```

De `*.csr` bestanden zijn niet nodig omdat het een tussenproduct is. Een
RSA sleutelpaar (`.key` en `.csr`) kan fysiek gescheiden van de CA gemaakt
worden. De CA ontvangt alleen de publieke sleutel in `.csr` en verifieert
de identiteit en sleutel. Daarna ondertekent de CA de publieke sleutel
en stuurt `.crt` terug.
In HiSPARC kunnen we de `.csr` bestanden dus weggooien. Ze bevatten geen
informatie die niet ook in het `.crt` certificaat staat.

Certificaten bekijken
=====================

Bekijk certificaat (vervaldatum, serie nummer, modulus):

```
openssl x509 -noout -text -in ca.crt
```

Controleer of de signature van een station/server certificaat
geldig is:

```
openssl verify -CAfile ca.crt sciencepark501.crt
openssl verify -CAfile ca.crt server.crt
```


Nieuw keys Maart 2018
=====================

Op 1 Maart 2018 verliep het root CA van het station VPN

```
cd /etc/openvpn/keys
openssl x509 -in ca.crt -days 36500 -out ca_new.crt -signkey ca.key
# vervang ca.crt door ca_new.crt en sla ca.key ergens veilig op.
```

Het oude root CA was 10 jaar geldig. Het nieuwe 100 jaar. Omdat het RSA sleutelpaar niet gewijzigd is, zijn signatures
van het oude CA ook nog geldig met het nieuwe. De station/server sleutels "doen het nog". (Tot ze zelf verlopen)

De server key verliep op dezelfde dag. We maken een nieuw
sleutelpaar:

```
# backup /etc/openvpn/keys/server*
# start een root shell:
cd /etc/openvpn/easy_rsa
# voeg COMMON_NAME=tietar.hisparc.nl toe aan `vars`
source ./vars
build-server-keys server
```
`/etc/openvpn/keys/server.*` zijn nu vervangen. Opslaan op
 veilige plek!

Doe hetzelfde voor het admin VPN:

```
cd /etc/openvpn/adminkeys
openssl x509 -in ca.crt -days 36500 -out ca_new.crt -signkey ca.key
# vervang ca.crt door ca_new.crt en sla ca.key ergens veilig op.
```

```
# backup /etc/openvpn/keys/server*
# start een root shell:
cd /etc/openvpn/easy_rsa
# voeg COMMON_NAME=server toe aan `vars-admin`
source ./vars-admin
build-server-keys server
```

`/etc/openvpn/adminkeys/server.*` zijn nu vervangen. Opslaan op veilige plek!

Zoeken naar certificaten die gaan verlopen
==========================================

Gebruik dit script: `checkdates.sh`
```
#!/usr/bin/env bash
for filename in $(find /etc/openvpn/keys/*.crt 2> /dev/null); do
    { date --date="$(openssl x509 -in $filename -noout -enddate  | cut -d= -f 2)" --iso-8601; echo "$filename";} | xargs -n 2
done
```
En sorteer:

```
> ./checkdates.sh | sort | head
2018-03-01 /etc/openvpn/keys/karel.crt
2018-06-07 /etc/openvpn/keys/pimu1.crt
2018-06-07 /etc/openvpn/keys/uva1.crt
2018-06-11 /etc/openvpn/keys/hal1.crt
2018-06-11 /etc/openvpn/keys/nikhef2.crt
2018-06-11 /etc/openvpn/keys/sara1.crt
2018-06-14 /etc/openvpn/keys/kascade1.crt
2018-06-24 /etc/openvpn/keys/hwc1.crt
2018-07-12 /etc/openvpn/keys/nikhef1.crt
2018-07-30 /etc/openvpn/keys/testdrive.crt

```

easy_rsa
========

`easy_rsa` is een verzameling script die OpenSSL gebruiken om de x509 PKI te runnen. (https://github.com/OpenVPN/easy-rsa)
We gebruiken een vendored (eigen) versie in `/etc/openvpn/easy_rsa` deze loopt zover achter op
de huidige versie van `easy_rsa` dat overstappen niet meer praktisch is.

MD5 -> SHA256 
=============

Er is een script `replace-key` in onze vendored `easy_rsa` waarmee je een nieuw certificaat `.crt` (publieke sleutel) kan maken
bij een bestaande geheime sleuel (`.key`). Dit is tegen de x509 standaard, maar maakt het mogelijk om een station (per email) een
nieuwe certificaat te sturen, waarmee ingelogd kan worden zonder het geheime deel te veranderen en uit te wisselen.

Keys op tietar?
===============
In a perfect world we would:
Store the root CA secret key on `pique` and let the STATION PC generate an RSA keypair and send it's certificate signing request (CSR) to an admin, while keeping it's secret key secret. An admin uses the admin interface on pique to create a PC object, and uploades the CSR to create a certificate signed with the root CA and stores the certificate (or just it's serial) in the database, to be able to revoke it. Keys are not in possession of the admins or on pique or tietar. hisparcvpnd is only used to add the new hostname to the hostfile on tietar. The admin then sends the certificate to the station pc, which can login because it owns the matching secret key.

TODO
====
