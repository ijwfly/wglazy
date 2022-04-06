echo installing dependencies...
apt update && apt install python3-venv wireguard wireguard-tools qrencode firewalld -y

echo init python3...
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo generating config...
python gen_config.py

echo configuring package forwarding...
sed -i '/net.ipv4.ip_forward/s/^#//g' /etc/sysctl.conf
sysctl -p

echo configuring firewall...
firewall-cmd --permanent --zone=public --add-port=35053/udp
firewall-cmd --permanent --zone=public --add-masquerade
firewall-cmd --reload

echo starting wireguard...
systemctl enable wg-quick@wg0.service
systemctl restart wg-quick@wg0.service
