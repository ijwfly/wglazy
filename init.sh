# install dependencies
apt update && apt install wireguard wireguard-tools qrencode -y

# init python3
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# generate server keys
wg genkey | tee keys/server_private_key | wg pubkey > keys/server_public_key
chmod 600 keys/*_private_key
