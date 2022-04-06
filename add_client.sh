source venv/bin/activate
python add_client.py

echo restarting wireguard...
systemctl restart wg-quick@wg0.service
