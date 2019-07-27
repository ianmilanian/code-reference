# OpenVPN
## Required Software
#### VPN Server (Ubuntu)
```
sudo apt-get update
sudo apt-get install openvpn easy-rsa
```
#### Windows Client
* [Putty](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html)
* [OpenVPN](https://openvpn.net/community-downloads/)
## Configuring Putty Client
#### Generating PPK Key
1. Convert aws key (.pem) to putty format (.ppk) using puttygen
2. Load .pem file in puttygen
3. Make sure rsa key type is selected
4. Choose save private key
#### Connecting to VPN Server
1. Start putty
2. Under session for hostname enter `ubuntu@x.x.x.x` (Public IP)
3. Under connection>ssh>auth browse and select .ppk file
4. Open
## Setup Certificate Authority
A *third party* that signs the server/client keys. The certificate authority should **NOT** reside on the VPN server ([see guide](https://help.ubuntu.com/lts/serverguide/openvpn.html.en)).
```
make-cadir ~/openvpn-ca
cd ~/openvpn-ca
ln -s openssl-1.0.0.cnf openssl.cnf
```
Modify the following fields inside the **_vars_** file.
```
export KEY_COUNTRY="XX"
export KEY_PROVINCE="XX"
export KEY_CITY="XX"
export KEY_ORG="XX"
export KEY_EMAIL="XX"
export KEY_OU="XX"
export KEY_NAME="server"
```
Export the environment variables we defined in the above step.
```
source vars
```
## Create Server Keys
**_Note_:** While executing build scripts entering nothing will use defaults set from previous step.
```
./clean-all
./build-ca
./build-key-server server
./build-dh
openvpn --genkey --secret keys/ta.key
sudo cp keys/server.crt keys/server.key keys/ca.crt keys/dh2048.pem keys/ta.key /etc/openvpn/
rm keys/server.* keys/*.pem
```
## Create Client Keys
**_Warning:_** Make sure to securely move zip folder to client machine and delete from server!
```
sudo adduser client
./build-key-pass client
tar -czvf client.tar.gz keys/client.crt keys/client.key keys/ca.crt keys/ta.key
rm keys/client.* keys/*.pem
```
## Server / Client Key Locations
| Filename | Needed By | Purpose | Secret |
| -------- | --------- | ------- | ------ |
| ca.crt | server + all clients | Root CA certificate | NO |
| ca.key | key signing machine only | Root CA key | YES |
| dh2048.pem | server only | Diffie Hellman parameters | NO |
| server.crt | server only | Server Certificate	| NO |
| server.key | server only | Server Key | YES |
| client1.crt | client1 only | Client1 Certificate | NO |
| client1.key | client1 only | Client1 Key | YES |
## Configuring VPN Server
```
sudo cp /usr/share/doc/openvpn/examples/sample-config-files/server.conf.gz /etc/openvpn/
sudo gzip -d /etc/openvpn/server.conf.gz
sudo nano /etc/openvpn/server.conf
```
Modify the following fields inside the **_server.conf_** file.
```
ca ca.crt
cert server.crt
key server.key
dh dh2048.pem
user nobody
group nogroup
plugin /usr/lib/x86_64-linux-gnu/openvpn/plugins/openvpn-plugin-auth-pam.so login
```
## Configuring Windows Client
1. Unzip **_client.tar.gz_** to the OpenVPN configuration folder.
2. Start the OpenVPN client and import the **_client.ovpn_** file from the OpenVPN configuration folder.
3. Open **_client.conf_** in notepad and modify the following lines:
```
remote x.x.x.x 1194
ca ca.crt
cert client.crt
key client.key
auth-user-pass
```
## VPN Server Commands
| Desc. | Command |
| ----------- | ------- |
| Start | `sudo systemctl start openvpn@server` |
| Stop | `sudo systemctl stop openvpn@server` |
| Debug | `sudo systemctl status openvpn@server` |
| Debug | `sudo journalctl -xe` |
