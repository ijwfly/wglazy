echo Enter client name:
read CLIENT_NAME

source venv/bin/activate
echo
echo $CLIENT_NAME | python add_client.py
echo
qrencode -t ansiutf8 -r configs/$CLIENT_NAME.conf

echo restarting wireguard...
systemctl restart wg-quick@wg0.service
