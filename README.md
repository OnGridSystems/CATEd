# OnGrid portal

# Installation
Start from clean Ubuntu 16 LTS installation

If your system has no swap partition you should make swap file to avoid low memory conditions

```sh
dd if=/dev/zero of=/swapfile bs=1M count=2000
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo "/swapfile   none    swap    sw    0   0" >> /etc/fstab
```

Upgrade packages and grub

```
echo -e "LC_ALL=en_US.UTF-8\nLANG=en_US.UTF-8" >> /etc/environment
read -d "" UPGRADESCRIPT <<"EOF"
export DEBIAN_FRONTEND=noninteractive
apt purge -y grub-pc grub-common
apt autoremove -y 
rm -rf /etc/grub.d/
apt -y update
apt upgrade -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" 
apt install -y openvpn git redis-server mysql-server libmysqlclient-dev libssl-dev openssl rabbitmq-server screen vim gcc make python3-pip python3-venv htop mc nginx supervisor libjpeg-dev libfreetype6-dev zlib1g-dev libxml2-dev libxslt1-dev
service supervisor restart  
apt install -y grub-pc grub-common
grub-install /dev/vda
update-grub
EOF
echo "$UPGRADESCRIPT" > /tmp/upgradescript
bash /tmp/upgradescript
```

and

```sh
reboot
```

After server bringup make SSH keys and settings

```sh
mkdir /root/.ssh
chmod 0755 /root/.ssh
touch /root/.ssh/id_rsa.pub
chmod 0644 /root/.ssh/id_rsa.pub
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDjRBWiF26Eb1pVsMl7Nxv2bplH+sHqbeSkDYuaWpryWNAs+070/qzoI4oo+8jybFf7yinhGb8msD0xU5a7c17aDnMI9f1AIKZIuBUaNp1rgH1R6ATJTXSQGK3YPl/Jncc9MNBoCyiKlpn/DVhmcTslECGGlFVfIHQT2rQh3qFNxhVK5R5SUBdxaxQ+pYKnABl0kzwb6bV+S7kHNPA8N5t95EFOsFQZ3JBTHZsqY2GPS8UBcKtmbixb/YcYm50CiypuiivnOec0CfbLPhssMhcAzpQuI3tKgdVa3It7/MVUlpXCC9q9xRyWvSd/ycKIBW0YZv1ZwWLB+3RlI0NnDtr1 root@portal" > /root/.ssh/id_rsa.pub
touch /root/.ssh/id_rsa
chmod 0600 /root/.ssh/id_rsa
read -d "" RSAID <<"EOF"
-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA40QVohduhG9aVbDJezcb9m6ZR/rB6m3kpA2Lmlqa8ljQLPtO
9P6s6COKKPvI8mxX+8op4Rm/JrA9MVOWu3Ne2g5zCPX9QCCmSLgVGjada4B9UegE
yU10kBit2D5fyZ3HPTDQaAsoipaZ/w1YZnE7JRAhhpRVXyB0E9q0Id6hTcYVSuUe
UlAXcWsUPqWCpwAZdJM8G+m1fku5BzTwPDebfeRBTrBUGdyQUx2bKmNhj0vFAXCr
Zm4sW/2HGJudAosqboor5znnNAn2yz4bLDIXAM6ULiN7SoHVWtyLe/zFVJaVwgva
vcUclr0nf8nCiAVtGGb9WcFiwft0ZSNDZw7a9QIDAQABAoIBADSj9I7S9ppeYIIw
rLqJjUSLYZ22i2wNgEQvjwJ1siYoRC/nFebRhqNOeBX+HBFq3wZHUWP+XrRLZiEi
x2sr0fCYIDUXJU3RQjLd0KV9uQDJhj2OjG1EL5eg38OSzwUYMqoNwHgY/Y78Szc0
lCFGYPi4v8s4WH3sOnbO1aJyutIUe9e0XozucWktVOyA8K1LcjBkwuHefOFxFUug
ooytB/zJJ4SqmBfvUJag+og5ZSStwu86SuacVbd/VAl4ecn2l+8cvQ9dwlkEWadN
N6QchnmBqn310EX1JSNX6aT579YP8s7abl+eJEVApOvj+W/9BYHIY+rR9QTQCOs1
Dp+E5RECgYEA+JFo1Yl3rjOcI55Jy1VMO6UzWnCFD9Q/CftLi6x/7WlRd81ZsjIc
ne8L14eBjXA5LnQoGwneUgxgI+QVuwiN/kgozoqDZ/DCaZlt4u5ouN55Q5NcX+G0
fH19w+9V3xeviKM2y9633D6IFz1+xFHiROU4q7JpZnXCi2jRtJojaE8CgYEA6g+f
7l637LjN00BnGLCLmmxMMjyJs8OVK8NLkuHjLb8Et5kuwJ+DXIkk+EzO2Z4uL0Id
jst5c5OYEPYdzwwg5IyRDdQQhgd3iThxdc6uiylHazBkg7O5IA67Ld3x5eaPnLCE
1LBLlWsUce2NNqx7s/3KUZl7vZVT/6n8zPx8M3sCgYBLnei3dU9cRkUMrN2kJrm/
N11s+Ofxzc6zmaf8wKhWMADhoi3UQNxly0/d7FIkFey/TgTZXOIuMaeZo4xczphr
r8YCNy8MkriB6XP9Yiuneb6IKS8j2ATRDlgRICEOciUrOwOzd3iVXsyFzWZgEMz1
yom36dmYmuBpCqUo/O8ijwKBgQCjiTM3O1rKvPyiY1clOwTvakd6ui2EOl0ZbKR7
BfTS26oSFadC0rDXkMMR8ah9CDZAsrMwOB6tkCwpfayqI1FAHq6iuM6qtsDgUV2E
8FmnxbmuvOsd0g7AxUom6/G9rfAdjH/ikyLcTSrFxzJpRu5Pfj1D8jcw6Qr9kOme
17J3zQKBgEtmtRZCru4F6lIqRHQ0LuKSWmQj5GMWpUQpAknU0FsYVuOARy2zG82r
Q96LKk79rktYZLJfSbBQFs2T0OOO55VHQ/SIm8zhYvCiCG/FGWZedtC1Je/HhZad
qrML3yarOYprFN8CupDTwbgIETx+DA5k1eUELraMiJcdx9Pme3H4
-----END RSA PRIVATE KEY-----
EOF
#
# Change SSH configuration to disable github key prompt
echo "$RSAID" > /root/.ssh/id_rsa
read -d "" SSHCFG <<"EOF"
Host github.com
    StrictHostKeyChecking no 
    UserKnownHostsFile /dev/null
    LogLevel QUIET
EOF
echo "$SSHCFG" >> /etc/ssh/ssh_config

```
Setup OpenVPN client (to poll rigs)
```
mkdir /etc/openvpn
read -d "" CACRT <<"EOF"
-----BEGIN CERTIFICATE-----
MIIE9DCCA9ygAwIBAgIJAL7JQUNNDavTMA0GCSqGSIb3DQEBCwUAMIGsMQswCQYD
VQQGEwJSVTEMMAoGA1UECBMDTU9XMQ8wDQYDVQQHEwZNb3Njb3cxFzAVBgNVBAoT
Dk9uR3JpZCBTeXN0ZW1zMRQwEgYDVQQLEwtPbkdyaWQgQ3JldzEaMBgGA1UEAxMR
T25HcmlkIFN5c3RlbXMgQ0ExEDAOBgNVBCkTB0Vhc3lSU0ExITAfBgkqhkiG9w0B
CQEWEm5vcmVwbHlAb25ncmlkLnBybzAeFw0xNzA3MDgxMTU5MTdaFw0yNzA3MDYx
MTU5MTdaMIGsMQswCQYDVQQGEwJSVTEMMAoGA1UECBMDTU9XMQ8wDQYDVQQHEwZN
b3Njb3cxFzAVBgNVBAoTDk9uR3JpZCBTeXN0ZW1zMRQwEgYDVQQLEwtPbkdyaWQg
Q3JldzEaMBgGA1UEAxMRT25HcmlkIFN5c3RlbXMgQ0ExEDAOBgNVBCkTB0Vhc3lS
U0ExITAfBgkqhkiG9w0BCQEWEm5vcmVwbHlAb25ncmlkLnBybzCCASIwDQYJKoZI
hvcNAQEBBQADggEPADCCAQoCggEBAMqEW8tvnRRHYFV+tFfvfOGTr40mQ3qEw/xa
Ge8u0lqq9iIUArt1gNF4HhCv9bgeUE+EkbLDh9aNKtRLA9Z+1JToyRnMoJp5dg1r
zEk+djArstoXx92Tla/+xY345Coo/pDKrWNUaQi34EtTZNB0TR2LvkiCFvZpxSWF
BbcY4oc/S4r6+cTy4hSz7coSll46ilFqeQgIi/KzDRqZFlVb75SylFVuLa9ngHmN
YyzwgioWhrfAtV4kcb1PI1MYN8An19/q/FCuX9vvGb/cV9EcCXtHtrVbQ7PLqpXa
jUfzZnVeBtFyhYqVn4goZkoko5JblsVOPmiDCsbtwU2t+TyDpr0CAwEAAaOCARUw
ggERMB0GA1UdDgQWBBSNOWvXw4Pu3kEQl+3JrTLDRbta6jCB4QYDVR0jBIHZMIHW
gBSNOWvXw4Pu3kEQl+3JrTLDRbta6qGBsqSBrzCBrDELMAkGA1UEBhMCUlUxDDAK
BgNVBAgTA01PVzEPMA0GA1UEBxMGTW9zY293MRcwFQYDVQQKEw5PbkdyaWQgU3lz
dGVtczEUMBIGA1UECxMLT25HcmlkIENyZXcxGjAYBgNVBAMTEU9uR3JpZCBTeXN0
ZW1zIENBMRAwDgYDVQQpEwdFYXN5UlNBMSEwHwYJKoZIhvcNAQkBFhJub3JlcGx5
QG9uZ3JpZC5wcm+CCQC+yUFDTQ2r0zAMBgNVHRMEBTADAQH/MA0GCSqGSIb3DQEB
CwUAA4IBAQAtIJk/WMLh0tw316IOsWyByIC0PKpqigE4sE4OMoSLlFiE44jNWNLc
KSMANlW4mqsC/c+HdSwJ1QvOGEgv0+9BnqdHi5byKrgWOOha7Z8exAFuvloA6PaN
udtiOHmYPmtMTTqUlMO6KmPvBRp1J5MzlqOFBawbczrBSAr6P8qGNXTppMx3nXr0
JQ9HEK7TML0fsIhbI1LZr0IhQg7zEXXNvc6ov4wFtkhPgZDmATU80ftSI1tYyxyA
VGs2YFk4ZOEpRyEn6pdQhq8s6uWxzbtX9C5A0wKvd8Rd5ErH2gTe406tVmcke2tj
Zvp5dXVc10KkHHYewZTDH5RgH73fggHg
-----END CERTIFICATE-----
EOF
echo "$CACRT" > /etc/openvpn/ca.crt

read -d "" PORTALCRT <<"EOF"
Certificate:
    Data:
        Version: 3 (0x2)
        Serial Number: 4 (0x4)
    Signature Algorithm: sha256WithRSAEncryption
        Issuer: C=RU, ST=MOW, L=Moscow, O=OnGrid Systems, OU=OnGrid Crew, CN=OnGrid Systems CA/name=EasyRSA/emailAddress=noreply@ongrid.pro
        Validity
            Not Before: Aug 16 06:47:33 2017 GMT
            Not After : Aug 14 06:47:33 2027 GMT
        Subject: C=RU, ST=MOW, L=Moscow, O=OnGrid Systems, OU=OnGrid Crew, CN=portal/name=EasyRSA/emailAddress=noreply@ongrid.pro
        Subject Public Key Info:
            Public Key Algorithm: rsaEncryption
                Public-Key: (2048 bit)
                Modulus:
                    00:c5:75:9a:a8:42:9a:6c:8e:2d:e4:3a:4a:61:ca:
                    5b:e3:c8:02:79:ec:0e:28:cd:6b:08:31:96:a8:dd:
                    94:9c:ad:bd:db:d6:4b:a3:f5:5f:79:d2:d7:7f:73:
                    d5:6a:2e:79:f9:05:1f:b6:7b:84:34:b9:a7:14:4e:
                    e4:76:0b:84:ff:a1:80:4c:d4:b3:ee:b5:0c:9e:50:
                    a9:ad:ec:a1:f7:4c:c0:63:18:c6:13:7f:38:dd:e5:
                    8c:d0:1b:2b:82:84:5c:b2:0e:39:f1:6f:12:48:42:
                    50:49:d1:d9:56:f3:b8:28:5d:bf:16:76:ef:c7:b4:
                    dc:38:12:36:a5:fc:76:f4:2e:2a:3c:e3:b4:89:d4:
                    a6:fa:69:48:ab:71:78:2f:e7:fd:da:a2:a0:a5:80:
                    90:51:31:fb:ea:b4:7a:62:f3:17:74:e1:11:b7:ea:
                    38:e7:d1:a9:6d:a5:39:f9:3f:07:54:ab:77:25:93:
                    dc:7a:c1:47:b8:5e:fd:36:d5:46:42:11:e2:91:d8:
                    6f:de:4b:fa:75:61:56:db:d5:61:b9:4c:5f:3f:9b:
                    92:cc:4a:f6:63:44:64:ba:fe:bf:c5:8e:49:14:0d:
                    0b:46:98:89:b2:dc:42:e3:2f:bf:94:9c:eb:c2:6c:
                    b5:40:40:e6:42:a5:95:17:e9:51:15:29:3c:5d:a0:
                    d1:41
                Exponent: 65537 (0x10001)
        X509v3 extensions:
            X509v3 Basic Constraints: 
                CA:FALSE
            Netscape Comment: 
                Easy-RSA Generated Certificate
            X509v3 Subject Key Identifier: 
                06:C0:7A:D9:A6:4A:0E:B0:2C:F1:61:EF:A0:AA:8D:EB:FB:47:2C:60
            X509v3 Authority Key Identifier: 
                keyid:8D:39:6B:D7:C3:83:EE:DE:41:10:97:ED:C9:AD:32:C3:45:BB:5A:EA
                DirName:/C=RU/ST=MOW/L=Moscow/O=OnGrid Systems/OU=OnGrid Crew/CN=OnGrid Systems CA/name=EasyRSA/emailAddress=noreply@ongrid.pro
                serial:BE:C9:41:43:4D:0D:AB:D3

            X509v3 Extended Key Usage: 
                TLS Web Client Authentication
            X509v3 Key Usage: 
                Digital Signature
            X509v3 Subject Alternative Name: 
                DNS:portal
    Signature Algorithm: sha256WithRSAEncryption
         4e:66:36:e0:50:0e:e2:3c:54:86:22:78:22:c3:e6:3f:97:1c:
         dc:83:71:6f:fe:bf:d1:60:7a:59:63:08:6e:07:94:9e:5c:ae:
         3b:89:39:1c:c3:b9:11:72:d6:73:48:b7:26:90:a9:3c:54:6b:
         90:fc:b8:e6:16:fe:d2:ab:6f:df:71:37:ca:c6:66:5c:7c:8a:
         e0:d5:4c:7f:db:cb:9c:62:12:ef:b3:85:35:6d:6a:b9:04:86:
         18:a3:f2:4b:34:9c:fb:e1:37:22:75:d8:0a:2b:c9:8d:5f:2a:
         88:da:fd:c8:5d:e9:31:73:42:22:1d:d2:06:d1:3f:2c:9c:c0:
         d9:11:f4:88:d9:16:73:21:71:f6:e1:aa:50:72:8d:44:53:79:
         41:c6:f8:12:db:9c:f3:e2:44:3b:6d:a4:d6:a2:57:4f:41:64:
         75:18:65:ef:17:cf:06:08:cc:5f:7a:63:54:f4:e4:31:84:82:
         c9:05:44:1c:14:96:85:8a:17:ba:d3:2e:42:6a:a3:5d:a7:04:
         43:5f:be:13:07:93:98:44:10:bf:01:cc:b5:c1:83:c7:72:13:
         9c:67:55:d6:2b:27:0f:ed:5f:b5:85:b4:3b:4b:d0:8f:fe:99:
         4b:17:d3:58:ee:77:fe:fb:81:e3:41:8e:90:b8:82:9b:57:72:
         4b:21:b7:fb
-----BEGIN CERTIFICATE-----
MIIFQjCCBCqgAwIBAgIBBDANBgkqhkiG9w0BAQsFADCBrDELMAkGA1UEBhMCUlUx
DDAKBgNVBAgTA01PVzEPMA0GA1UEBxMGTW9zY293MRcwFQYDVQQKEw5PbkdyaWQg
U3lzdGVtczEUMBIGA1UECxMLT25HcmlkIENyZXcxGjAYBgNVBAMTEU9uR3JpZCBT
eXN0ZW1zIENBMRAwDgYDVQQpEwdFYXN5UlNBMSEwHwYJKoZIhvcNAQkBFhJub3Jl
cGx5QG9uZ3JpZC5wcm8wHhcNMTcwODE2MDY0NzMzWhcNMjcwODE0MDY0NzMzWjCB
oTELMAkGA1UEBhMCUlUxDDAKBgNVBAgTA01PVzEPMA0GA1UEBxMGTW9zY293MRcw
FQYDVQQKEw5PbkdyaWQgU3lzdGVtczEUMBIGA1UECxMLT25HcmlkIENyZXcxDzAN
BgNVBAMTBnBvcnRhbDEQMA4GA1UEKRMHRWFzeVJTQTEhMB8GCSqGSIb3DQEJARYS
bm9yZXBseUBvbmdyaWQucHJvMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKC
AQEAxXWaqEKabI4t5DpKYcpb48gCeewOKM1rCDGWqN2UnK2929ZLo/VfedLXf3PV
ai55+QUftnuENLmnFE7kdguE/6GATNSz7rUMnlCpreyh90zAYxjGE3843eWM0Bsr
goRcsg458W8SSEJQSdHZVvO4KF2/Fnbvx7TcOBI2pfx29C4qPOO0idSm+mlIq3F4
L+f92qKgpYCQUTH76rR6YvMXdOERt+o459GpbaU5+T8HVKt3JZPcesFHuF79NtVG
QhHikdhv3kv6dWFW29VhuUxfP5uSzEr2Y0Rkuv6/xY5JFA0LRpiJstxC4y+/lJzr
wmy1QEDmQqWVF+lRFSk8XaDRQQIDAQABo4IBdjCCAXIwCQYDVR0TBAIwADAtBglg
hkgBhvhCAQ0EIBYeRWFzeS1SU0EgR2VuZXJhdGVkIENlcnRpZmljYXRlMB0GA1Ud
DgQWBBQGwHrZpkoOsCzxYe+gqo3r+0csYDCB4QYDVR0jBIHZMIHWgBSNOWvXw4Pu
3kEQl+3JrTLDRbta6qGBsqSBrzCBrDELMAkGA1UEBhMCUlUxDDAKBgNVBAgTA01P
VzEPMA0GA1UEBxMGTW9zY293MRcwFQYDVQQKEw5PbkdyaWQgU3lzdGVtczEUMBIG
A1UECxMLT25HcmlkIENyZXcxGjAYBgNVBAMTEU9uR3JpZCBTeXN0ZW1zIENBMRAw
DgYDVQQpEwdFYXN5UlNBMSEwHwYJKoZIhvcNAQkBFhJub3JlcGx5QG9uZ3JpZC5w
cm+CCQC+yUFDTQ2r0zATBgNVHSUEDDAKBggrBgEFBQcDAjALBgNVHQ8EBAMCB4Aw
EQYDVR0RBAowCIIGcG9ydGFsMA0GCSqGSIb3DQEBCwUAA4IBAQBOZjbgUA7iPFSG
Ingiw+Y/lxzcg3Fv/r/RYHpZYwhuB5SeXK47iTkcw7kRctZzSLcmkKk8VGuQ/Ljm
Fv7Sq2/fcTfKxmZcfIrg1Ux/28ucYhLvs4U1bWq5BIYYo/JLNJz74TciddgKK8mN
XyqI2v3IXekxc0IiHdIG0T8snMDZEfSI2RZzIXH24apQco1EU3lBxvgS25zz4kQ7
baTWoldPQWR1GGXvF88GCMxfemNU9OQxhILJBUQcFJaFihe60y5CaqNdpwRDX74T
B5OYRBC/Acy1wYPHchOcZ1XWKycP7V+1hbQ7S9CP/plLF9NY7nf++4HjQY6QuIKb
V3JLIbf7
-----END CERTIFICATE-----
EOF
echo "$PORTALCRT" > /etc/openvpn/portal.crt

read -d "" KEY <<"EOF"
-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDFdZqoQppsji3k
OkphylvjyAJ57A4ozWsIMZao3ZScrb3b1kuj9V950td/c9VqLnn5BR+2e4Q0uacU
TuR2C4T/oYBM1LPutQyeUKmt7KH3TMBjGMYTfzjd5YzQGyuChFyyDjnxbxJIQlBJ
0dlW87goXb8Wdu/HtNw4Ejal/Hb0Lio847SJ1Kb6aUircXgv5/3aoqClgJBRMfvq
tHpi8xd04RG36jjn0altpTn5PwdUq3clk9x6wUe4Xv021UZCEeKR2G/eS/p1YVbb
1WG5TF8/m5LMSvZjRGS6/r/FjkkUDQtGmImy3ELjL7+UnOvCbLVAQOZCpZUX6VEV
KTxdoNFBAgMBAAECggEAcu0AFu6s8oHONAe5QzGESg8fYdcCZr0ojpxOE/rjhE2b
M1iGreciqsUMqCHDFQn38/gHfS5mxElJ9Yf1cL9DqYVWJ2GlWEoIDhzkpVYU7tq9
HvBMWQyzDHOOgZFOwahIS1n8X4lGGsh98nkxBmrTxKrLjUesR4/8nKX9KJ7InVU7
aj1FUDXM9Q2XV/KFcDmx2ZNbv5oPbaLnsUwnKDANmYmkROIpWcrLN8VNq14balXI
1lR3Q3ddYL7XlD5dKWQ0aoUIVzCDKa4ZTUI4/uULBQgeZypvXmnIZmQCkHWLmfAS
9l4fu8boVuFSZ83zOpfx4mHuSisPK86WZ82pPZxkAQKBgQDnpvgu92IsxShXUbXj
AmUeEm773C7VPr85iwJECr/ouhhrHA3a5CtkOYoauMd1lnNY5ZAM4dBn9HMvxNqz
vWFleWtrxQTFzXBlK3IbnAlwnqeNDU7SrQoDCtD9WrzGtXhb1XjmlYJE40xt7ptC
XoAbgl+Y2jb25aPntYkyotfPqwKBgQDaNp0HMx/P05J4Zo1s/46sG+zXxfOQEUBc
cIeGUL39RO/AtnLScbBUpkAGcSPD8QDLe/PTu2t/0XoHTcBBEf7kg2w+wUW9gBgC
5sDelwviv8A9sngfW22qK5XcRDawp6FFFwW3juruViigMPUGHIwWV/LNHKonECN2
wOLuKf7mwwKBgAcoYJjK6gyqFuID01PtWgSA208K8aODKdN0WSCTGHTvcxu0JTVz
QWf6YysKNJeMi4nepgHP5Gmh4wFB2uQc4OqKwuf0kX4vJ97oZcE2pBAHxvOTyrC1
yg5oAich651UNCDaSr8NNZY9U7o92ixF0T2IXL3TWElutQ7OzCt1Xqe7AoGARJSH
c3zQ0atHzElGx2vl9hdsrz/KVYvmc2b2YPM9Urz4sNNmcNdEOMZrNtsWB33V5x3U
usWbendmZ6c69fhm6ICZY3uwpGb+pOLK2OoV1TS4gWt2rzw30hSSq8BQg+KbH7Cl
nlPvZ+pyKC5aw4nzSQ5pA6evnklHLAphB8LxFqsCgYBtMuE94bsumdY9OIDEgdD4
UdRnPb9xLqrjc7cAkw7mvPeXO5j+WoCiwwrB11Soq1Ub3+MWbqdYv7+iLoCmnKa7
KwlJFN0En1omu7b3tQ51U3UnQkSUmMku2S/qzzjg1AOZwo3skA462oBIv84FSSvF
H8Rmu/kJmSK8tbtkilGlHQ==
-----END PRIVATE KEY-----
EOF
echo "$KEY" > /etc/openvpn/portal.key

read -d "" OVPNCFG <<"EOF"
client
dev tun
proto tcp
remote vpn.ongrid.pro 1194
resolv-retry infinite
ca ca.crt
cert portal.crt
key portal.key
cipher AES-256-CBC
verb 3
EOF
echo "$OVPNCFG" > /etc/openvpn/client.conf
systemctl restart openvpn@client
```
Insert into hosts rigs names
```
echo "192.168.199.200 dialog-gw dlg-gw" > /etc/hosts
echo "192.168.200.1 dlg-gw-internal" > /etc/hosts
echo "192.168.200.2 dlg-wifi" > /etc/hosts
echo "192.168.200.101 dlg-r01" > /etc/hosts
echo "192.168.200.102 dlg-r02" > /etc/hosts
echo "192.168.200.103 dlg-r03" > /etc/hosts
echo "192.168.200.104 dlg-r04" > /etc/hosts
echo "192.168.200.105 dlg-r05" > /etc/hosts
echo "192.168.200.106 dlg-r06" > /etc/hosts
echo "192.168.200.107 dlg-r07" > /etc/hosts
echo "192.168.200.108 dlg-r08" > /etc/hosts
echo "192.168.200.109 dlg-r09" > /etc/hosts
echo "192.168.200.110 dlg-r10" > /etc/hosts
echo "192.168.199.201 him-gw" > /etc/hosts
echo "192.168.201.1 h1-gw-internal" > /etc/hosts
echo "192.168.201.2 him-wifi" > /etc/hosts
echo "192.168.201.101 h1-r01" > /etc/hosts
echo "192.168.201.102 h1-r02" > /etc/hosts
echo "192.168.201.103 h1-r03" > /etc/hosts
echo "192.168.201.104 h1-r04" > /etc/hosts
echo "192.168.201.105 h1-r05" > /etc/hosts
echo "192.168.201.106 h1-r06" > /etc/hosts
echo "192.168.201.107 h1-r07" > /etc/hosts
echo "192.168.201.108 h1-r08" > /etc/hosts
echo "192.168.201.109 h1-r09" > /etc/hosts
echo "192.168.201.110 h1-r10" > /etc/hosts
echo "192.168.201.151 h1-gn01" > /etc/hosts
echo "192.168.202.1 h1-gw-internal" > /etc/hosts
echo "192.168.202.101 h2-r01" > /etc/hosts
echo "192.168.202.102 h2-r02" > /etc/hosts
echo "192.168.202.103 h2-r03" > /etc/hosts
echo "192.168.202.104 h2-r04" > /etc/hosts
echo "192.168.202.105 h2-r05" > /etc/hosts
echo "192.168.202.106 h2-r06" > /etc/hosts
echo "192.168.202.107 h2-r07" > /etc/hosts
echo "192.168.202.108 h2-r08" > /etc/hosts
echo "192.168.202.109 h2-r09" > /etc/hosts
echo "192.168.202.110 h2-r10" > /etc/hosts

```
Install python virtualenv, create configs, clone project from git and apply some patches

```sh
cd /opt
mkdir portal_ongrid
cd portal_ongrid
mkdir logs static media configs
python3 -m venv env
cd /opt/portal_ongrid/configs

#
#set config for gunicorn
read -d "" DJTRD<<"EOF"
#!/bin/sh

NAME="djangoTrade"                                  
DJANGODIR=/opt/portal_ongrid/ongrid_portal/             
USER=root                                        
GROUP=root                                     
NUM_WORKERS=2                                    
DJANGO_SETTINGS_MODULE=djangoTrade.settings            
DJANGO_WSGI_MODULE=djangoTrade.wsgi                     
echo "Starting $NAME as `whoami`"
cd $DJANGODIR
source ../env/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR
exec ../env/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user=$USER --group=$GROUP \
  --bind="127.0.0.1:9023" \
  --log-level=debug \
  --log-file=-
EOF
echo "$DJTRD" > /opt/portal_ongrid/configs/djangoTrade
chmod u+x /opt/portal_ongrid/configs/djangoTrade

#
#set config for nginx
read -d "" NGINX <<"EOF"
server {
  listen 80;
  server_name  portal.ongrid.pro www.portal.ongrid.pro;
  rewrite  ^(.*) https://$server_name$1 permanent;
}
server {
    listen 443 ssl;
    server_name 127.0.0.1 portal.ongrid.pro www.portal.ongrid.pro;
    access_log  /opt/portal_ongrid/logs/nginx_access.log;
    client_max_body_size 100M;
    keepalive_timeout    60;
    ssl_certificate      /etc/letsencrypt/ongrid.crt;
    ssl_certificate_key  /etc/letsencrypt/private.key;
    ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
    ssl_ciphers  "HIGH:!RC4:!aNULL:!MD5:!kEDH";
    add_header Strict-Transport-Security 'max-age=604800';
   
    location /.well-known {
        alias /.well-known;
    }
    location /media  {
        alias /opt/portal_ongrid/media;
        expires 30d;
        add_header Pragma public;
        add_header Cache-Control "public";
    }
    location /static {
        alias /opt/portal_ongrid/static;
        expires 30d;
        add_header Pragma public;
        add_header Cache-Control "public";
    }

    location / {
        proxy_pass http://127.0.0.1:9023;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_connect_timeout       600;
        proxy_send_timeout          600;
        proxy_read_timeout          600;
        send_timeout                600;
    }
  }
EOF
echo "$NGINX" > /opt/portal_ongrid/configs/nginx.conf

#
#set config for supervisor
read -d "" VISOR <<"EOF"
[program:djangoTrade_web]
command = /opt/portal_ongrid/configs/djangoTrade
user = root
stdout_logfile = /opt/portal_ongrid/logs/gunicorn_supervisor.log
redirect_stderr = true
environment=LANG=en_US.UTF-8,LC_ALL=en_US.UTF-8
EOF
echo "$VISOR" > /opt/portal_ongrid/configs/supervisor.conf

cd /opt/portal_ongrid
source /opt/portal_ongrid/env/bin/activate
pip install --upgrade pip setuptools wheel
git clone -b feature-ccxt git@github.com:ongrid/ongrid_portal.git
cd ongrid_portal
pip install gunicorn
pip install -r requirements.txt

#
#patching configuration
read -d "" PATCH <<"EOF"
20c20
< CELERY_RESULT_BACKEND = 'db+mysql://root:123@localhost/celery_result'
---
> CELERY_RESULT_BACKEND = 'db+mysql://ongrid:lGG%tts%QP@localhost/celery_result'
64c64
< DEBUG = True
---
> DEBUG = False
66c66
< ALLOWED_HOSTS = ['127.0.0.1', '192.168.254.247']
---
> ALLOWED_HOSTS = ['portal.ongrid.pro', 'www.portal.ongrid.pro']
143,145c143,145
<         'NAME': 'tradenew',
<         'USER': 'root',
<         'PASSWORD': '123',
---
>         'NAME': 'trade',
>         'USER': 'ongrid',
>         'PASSWORD': 'lGG%tts%QP',
188c188
< YANDEX_MONEY_REDIRECT_URI = 'http://78.155.218.16:8000/wallet/'
---
> YANDEX_MONEY_REDIRECT_URI = 'http://portal.ongrid.pro/wallet/'
190c190
< YANDEX_MONEY_CLIENT_SECRET = '211A8533870D422A3EAB307B20897DB1A76EFD1379263CFD69FEC67630EA304A4831D7813BDEC90A866ABED2C30B9F8578EFF29962B13B70187429034EA3BF59'
---
> YANDEX_MONEY_CLIENT_SECRET = 'DD89A956C22739F77FDA276D64E9DF2E711DAA7645BFA5741872C0DA93DA8240EDDB6FBD2500210891396231AF4FB5B2FD90C7C0BB45F51803EAA36105CE508F'
EOF
echo "$PATCH" | patch djangoTrade/settings.py



read -d "" SENPATCH <<"EOF"
329c329
< @celeryd_init.connect(sender='worker_high@')
---
> @celeryd_init.connect(sender='worker_high@_HOSTNAME_')
EOF
SENPATCH=`echo "$SENPATCH" | sed -e "s/_HOSTNAME_/$HOSTNAME/g"`
echo "$SENPATCH" | patch /opt/portal_ongrid/ongrid_portal/tradeBOT/tasks.py
```

set databases and mocks

```sh
echo "create database trade character set utf8;" | mysql -u root
echo "create database celery_result;" | mysql -u root
echo "CREATE USER 'ongrid'@'localhost' IDENTIFIED BY 'lGG%tts%QP';" | mysql -u root
echo "GRANT ALL PRIVILEGES ON *.* TO 'ongrid'@'localhost';" | mysql -u root
echo "FLUSH PRIVILEGES;" | mysql -u root
#
# Migrate
./manage.py makemigrations 
./manage.py makemigrations trade
./manage.py makemigrations tradeBOT
./manage.py makemigrations monitoring
./manage.py migrate
#
# Add main data
read -d "" ADDMAIN<<"EOF"
from trade import models as trade_m
from monitoring import models as monit_m
trade_m.Exchanges.objects.get_or_create(name='poloniex', info_frozen_key='-isFrozen')
trade_m.Wallets.objects.get_or_create(name='BTC')
trade_m.Wallets.objects.get_or_create(name='ETH')
trade_m.Wallets.objects.get_or_create(name='Yandex Money')
monit_m.Pools.objects.get_or_create(pool='nanopool')
monit_m.Pools.objects.get_or_create(pool='ethermine')
EOF
echo "$ADDMAIN" | ./manage.py shell
#
# Add users
read -d "" PYCODE <<"EOF"
from django.contrib.auth.models import User
user = User.objects.create_user(username='kirill',
                                 email='kirill@ongrid.pro',
                                 password='kirill')
EOF
echo "$PYCODE" | ./manage.py shell
ln -s /opt/portal_ongrid/configs/supervisor.conf /etc/supervisor/conf.d/djangoTrade.conf
ln -s /opt/portal_ongrid/configs/nginx.conf /etc/nginx/sites-enabled/portal_ongrid.conf
supervisorctl update
supervisorctl restart djangoTrade_web
./manage.py collectstatic --noinput
```

install and configure celery

```sh
useradd -m celery
mkdir /var/log/celery
mkdir /var/run/celery
chown -R celery:celery /var/log/celery
chown -R celery:celery /var/run/celery

wget https://raw.githubusercontent.com/celery/celery/4.0/extra/generic-init.d/celeryd -O /etc/init.d/celeryd
wget https://raw.githubusercontent.com/celery/celery/4.0/extra/generic-init.d/celerybeat -O /etc/init.d/celerybeat
chmod +x /etc/init.d/celeryd /etc/init.d/celerybeat

#add celery config
read -d "" CELERYD_CFG <<"EOF"
CELERYD_NODES="worker_set_orders worker_low worker_normal worker_high"
CELERY_BIN="/opt/portal_ongrid/env/bin/python -m celery"
CELERY_APP="djangoTrade"
CELERYD_CHDIR="/opt/portal_ongrid/ongrid_portal"
CELERYD_OPTS="-Q:worker_set_orders set_orders -Q:worker_low low -Q:worker_normal normal -Q:worker_high high -c:worker_set_orders 1 -c:worker_low 3 -c:worker_normal 3 -c:worker_high 2"
CELERYD_LOG_FILE="/var/log/celery/%n%I.log"
CELERYD_PID_FILE="/var/run/celery/%n.pid"
CELERYD_USER="celery"
CELERYD_GROUP="celery"
DJANGO_SETTINGS_MODULE="djangoTrade.settings"
CELERY_CREATE_DIRS=1
SECRET_KEY="ada#qadaa2d#1232%!^&#*(&@(!&Y!&#*T!@(^F#!@&#F!@&#F!(@"
EOF
echo "$CELERYD_CFG" > /etc/default/celeryd

read -d "" CELERYBEAT_CFG <<"EOF"
CELERY_BIN="/opt/portal_ongrid/env/bin/python -m celery"
CELERY_APP="djangoTrade"
CELERYD_CHDIR="/opt/portal_ongrid/ongrid_portal"
DJANGO_SETTINGS_MODULE="djangoTrade.settings"
EOF
echo "$CELERYBEAT_CFG" > /etc/default/celerybeat

/etc/init.d/celeryd create-paths
/etc/init.d/celeryd start
/etc/init.d/celeryd stop
sudo update-rc.d celeryd defaults
sudo update-rc.d celerybeat defaults
```

Set SSL certificate (12.10.2017, 13:00:00)
```sh
cd /etc
mkdir letsencrypt
cd letsencrypt
read -d "" CERT<<"EOF"
-----BEGIN CERTIFICATE-----
MIIFBTCCA+2gAwIBAgISA3/inLnXFdE7eV6iZy15zN83MA0GCSqGSIb3DQEBCwUA
MEoxCzAJBgNVBAYTAlVTMRYwFAYDVQQKEw1MZXQncyBFbmNyeXB0MSMwIQYDVQQD
ExpMZXQncyBFbmNyeXB0IEF1dGhvcml0eSBYMzAeFw0xNzA3MTQxMDAwMDBaFw0x
NzEwMTIxMDAwMDBaMBwxGjAYBgNVBAMTEXBvcnRhbC5vbmdyaWQucHJvMIIBIjAN
BgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvft5fOL9fwj91Sx+VePqQuNPUMYE
O04+y0lz5QpPI6EWseDQrRzBbG50L+CenBd9w96jgSaQW+6D7Dj6sGJAMJwbT/5u
sai+ZFStgFsEkAKVBx3RnxUo8ihFllndG8uKu8M3q3iRZk6a4nz+TznENVAkwRpf
V6FZNVuth2QTFNmGdTNbli7672YIcactnQxGdSra6t6OFZhk1i+olugKTEKgaD0l
VXy5uDfMTstd5DcEVqkOvaeJaxkDXnhDmRIV4v9rYeveOCB+35wGOvuY4S7Xy6VV
uQagwhn0jfaJ90L0Jtj8/9USWqTqVq9upja+g3AjfS7jkQSVoWH5s2dyRQIDAQAB
o4ICETCCAg0wDgYDVR0PAQH/BAQDAgWgMB0GA1UdJQQWMBQGCCsGAQUFBwMBBggr
BgEFBQcDAjAMBgNVHRMBAf8EAjAAMB0GA1UdDgQWBBQufjoegphavRu105iUzhBe
F3ENWjAfBgNVHSMEGDAWgBSoSmpjBH3duubRObemRWXv86jsoTBvBggrBgEFBQcB
AQRjMGEwLgYIKwYBBQUHMAGGImh0dHA6Ly9vY3NwLmludC14My5sZXRzZW5jcnlw
dC5vcmcwLwYIKwYBBQUHMAKGI2h0dHA6Ly9jZXJ0LmludC14My5sZXRzZW5jcnlw
dC5vcmcvMBwGA1UdEQQVMBOCEXBvcnRhbC5vbmdyaWQucHJvMIH+BgNVHSAEgfYw
gfMwCAYGZ4EMAQIBMIHmBgsrBgEEAYLfEwEBATCB1jAmBggrBgEFBQcCARYaaHR0
cDovL2Nwcy5sZXRzZW5jcnlwdC5vcmcwgasGCCsGAQUFBwICMIGeDIGbVGhpcyBD
ZXJ0aWZpY2F0ZSBtYXkgb25seSBiZSByZWxpZWQgdXBvbiBieSBSZWx5aW5nIFBh
cnRpZXMgYW5kIG9ubHkgaW4gYWNjb3JkYW5jZSB3aXRoIHRoZSBDZXJ0aWZpY2F0
ZSBQb2xpY3kgZm91bmQgYXQgaHR0cHM6Ly9sZXRzZW5jcnlwdC5vcmcvcmVwb3Np
dG9yeS8wDQYJKoZIhvcNAQELBQADggEBAH1yiifbBsnv9KV9Pxmdo8+ZR2UgqCHp
Z4FrcENBWleHpDopPvd0h7Jsxa6IkjvM4JA0ITrC9ZMckQUPfcmBzC/13efPjtl6
VcGBGQmfiNWvoAvpKF7cYOHGZ6LQfQ5M3wKfTC27si/vwaeL0277yO1EpcG/ZJYx
LCYnE0TFN5+EFIGpneAolGu30Rxpe86IFcEH+KhW2k6vwrlbpN/XF9ENvTTu740T
WsGSo6XtYfhr2gPQi/glC605TnN3Jv/fSXKxvKj6hMMb3FpANqZBPuAKfrsXudxY
yGN6qyNB2XeJV1IeHD9HeFTmaRx++SYybGDIwUKbFDWuHF1iN2PGZu4=
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIEkjCCA3qgAwIBAgIQCgFBQgAAAVOFc2oLheynCDANBgkqhkiG9w0BAQsFADA/
MSQwIgYDVQQKExtEaWdpdGFsIFNpZ25hdHVyZSBUcnVzdCBDby4xFzAVBgNVBAMT
DkRTVCBSb290IENBIFgzMB4XDTE2MDMxNzE2NDA0NloXDTIxMDMxNzE2NDA0Nlow
SjELMAkGA1UEBhMCVVMxFjAUBgNVBAoTDUxldCdzIEVuY3J5cHQxIzAhBgNVBAMT
GkxldCdzIEVuY3J5cHQgQXV0aG9yaXR5IFgzMIIBIjANBgkqhkiG9w0BAQEFAAOC
AQ8AMIIBCgKCAQEAnNMM8FrlLke3cl03g7NoYzDq1zUmGSXhvb418XCSL7e4S0EF
q6meNQhY7LEqxGiHC6PjdeTm86dicbp5gWAf15Gan/PQeGdxyGkOlZHP/uaZ6WA8
SMx+yk13EiSdRxta67nsHjcAHJyse6cF6s5K671B5TaYucv9bTyWaN8jKkKQDIZ0
Z8h/pZq4UmEUEz9l6YKHy9v6Dlb2honzhT+Xhq+w3Brvaw2VFn3EK6BlspkENnWA
a6xK8xuQSXgvopZPKiAlKQTGdMDQMc2PMTiVFrqoM7hD8bEfwzB/onkxEz0tNvjj
/PIzark5McWvxI0NHWQWM6r6hCm21AvA2H3DkwIDAQABo4IBfTCCAXkwEgYDVR0T
AQH/BAgwBgEB/wIBADAOBgNVHQ8BAf8EBAMCAYYwfwYIKwYBBQUHAQEEczBxMDIG
CCsGAQUFBzABhiZodHRwOi8vaXNyZy50cnVzdGlkLm9jc3AuaWRlbnRydXN0LmNv
bTA7BggrBgEFBQcwAoYvaHR0cDovL2FwcHMuaWRlbnRydXN0LmNvbS9yb290cy9k
c3Ryb290Y2F4My5wN2MwHwYDVR0jBBgwFoAUxKexpHsscfrb4UuQdf/EFWCFiRAw
VAYDVR0gBE0wSzAIBgZngQwBAgEwPwYLKwYBBAGC3xMBAQEwMDAuBggrBgEFBQcC
ARYiaHR0cDovL2Nwcy5yb290LXgxLmxldHNlbmNyeXB0Lm9yZzA8BgNVHR8ENTAz
MDGgL6AthitodHRwOi8vY3JsLmlkZW50cnVzdC5jb20vRFNUUk9PVENBWDNDUkwu
Y3JsMB0GA1UdDgQWBBSoSmpjBH3duubRObemRWXv86jsoTANBgkqhkiG9w0BAQsF
AAOCAQEA3TPXEfNjWDjdGBX7CVW+dla5cEilaUcne8IkCJLxWh9KEik3JHRRHGJo
uM2VcGfl96S8TihRzZvoroed6ti6WqEBmtzw3Wodatg+VyOeph4EYpr/1wXKtx8/
wApIvJSwtmVi4MFU5aMqrSDE6ea73Mj2tcMyo5jMd6jmeWUHK8so/joWUoHOUgwu
X4Po1QYz+3dszkDqMp4fklxBwXRsW10KXzPMTZ+sOPAveyxindmjkW8lGy+QsRlG
PfZ+G6Z6h7mjem0Y+iWlkYcV4PIWL1iwBi8saCbGS5jN2p8M+X+Q7UNKEkROb3N6
KOqkqm57TH2H3eDJAkSnh6/DNFu0Qg==
-----END CERTIFICATE-----
EOF
echo "$CERT" > /etc/letsencrypt/ongrid.crt

read -d "" KEY<<"EOF"
-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC9+3l84v1/CP3V
LH5V4+pC409QxgQ7Tj7LSXPlCk8joRax4NCtHMFsbnQv4J6cF33D3qOBJpBb7oPs
OPqwYkAwnBtP/m6xqL5kVK2AWwSQApUHHdGfFSjyKEWWWd0by4q7wzereJFmTpri
fP5POcQ1UCTBGl9XoVk1W62HZBMU2YZ1M1uWLvrvZghxpy2dDEZ1Ktrq3o4VmGTW
L6iW6ApMQqBoPSVVfLm4N8xOy13kNwRWqQ69p4lrGQNeeEOZEhXi/2th6944IH7f
nAY6+5jhLtfLpVW5BqDCGfSN9on3QvQm2Pz/1RJapOpWr26mNr6DcCN9LuORBJWh
YfmzZ3JFAgMBAAECggEAD98JWDCSYuF6ayurZjuDH5Fj1+ijA91Wi58YSoMg92YG
wld4t22WjxtvI2zNc1bXD9zypeB14Og9JyffcYrTt/vioD0uPDNPrIwSbo2sBOfi
UVThZTvcTtakcZoSSbcoYOU/KlkJNJXOhKtSh4XY6WdHmsY8PtLg4/9DsPLgUTZy
Et8Tt4ozlPRXNRyb+7LbR3Rg1FWc6hfYSVh8eUYwZeoNlyN12CbAhZQ878DApHTi
CUu97UGqbOzeM/DpJzXDz7tDC5K3eMJetFPSwOBqmHQhTWdx9YuVVmA7gXmLKdJ4
4HQvGUaVo8PV1iDLnFq1TNFGUYjYIdjDD4cOwDlS4QKBgQDjRlDci0zHZ8O1ub/O
B4DiDH6pvKzGov08D8GlrnvmdN0XYEgoKSBYm2nqhaJwBHGmb08dqA6E7gpxS0sM
uOvoSA8wOOP2YlJJDcQlMQJe+0vjnmguZgNSEAn8RxoxEhO0vXEz4tyrIqMQ6PDV
pkRRi31aBA67cx4A8yCZJZyKbQKBgQDV/oeqK9oPSPtjt5XGt8diPlNuokYbcFOC
HugO459DBi4mdM6l8OdQB8Y8fygRrlK9bAOdtwZ+LAL3+DEjO0jHLpjB4LUYWQQN
wyL39uNqNH/ikhuQe8Kxf0Gt2g11xkto+6lceQ025sQxtaD3Hdtv18x8YM3I4p3U
ZfZFU9sgOQKBgQDFCACyMlGtzddthEs0Ymzpi8uDe36N9l9z4nUPHeVsNYQ279Ge
f4j7SEDagGACnNeqYnVEUJ3FwFhtP8kgjnB2P4JrW+bFgxezHaweUg6sKU/xVTMc
hnP6gM0nWLzsLa/H0TSCtvp3ot+bmVaw4iP4TeWuVDYxa+tnB2ALZQABQQKBgCuU
ycZTZfaE84WsZtlwpi+Q5+b5L3P5HVi7uKEHpHC++nkkgs1y0XkQDERX1S48pWck
b1wYYT8i8XvU1RUKxtih2cRqYhdSUawH2MBNTKVdicn33ZtASTdi5lpktScOOl9o
GWbW1GUg/EXvapfJQd52QZP3FxHZbTFLjqsx18epAoGAYSFs3ZLMfGI7CxdDeZUu
RHxfhHB8LCneUa3NaavfYAGB5OZMSHA88yKPh6/zQiVnAjv5FnzVFXExyIXdMh0y
hj7NDwUGVs3OAYZwa2GVPZJ9iiKq0wD+kdZV3Xk2BxAuU+NOvNrT3f2Z6KR0Xe5O
kyP/Ua+Xu2maz/FBXmJtd2I=
-----END PRIVATE KEY-----
EOF
echo "$KEY" > /etc/letsencrypt/private.key
```

reboot

```sh
cd /opt/portal_ongrid/ongrid_portal
. ../env/bin/activate
read -d "" PYTASKS <<"EOF"
from tradeBOT import tasks
coinmarketcup = tasks.pull_coinmarketcup.delay()
EOF
echo "$PYTASKS" | ./manage.py shell
```

reboot and have fun!

