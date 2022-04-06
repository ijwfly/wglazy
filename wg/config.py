import json
import urllib.request
from typing import List, Dict

from ipaddress import IPv4Network
from pydantic import BaseModel

from wg.wireguard import WireGuardController

DEFAULT_NETWORK = "10.8.0.0/24"
DEFAULT_DNS = "1.1.1.1"
DEFAULT_CONFIG_PATH = "config.json"
DEFAULT_WG_CONFIG_PATH = "/etc/wireguard/wg0.conf"
DEFAULT_WG_CLIENTS_PATH = "configs/"


class WgClientConfig(BaseModel):
    name: str
    local_address: str
    private_key: str
    public_key: str
    allowed_ips: str
    persistent_keepalive: int


class WgServerConfig(BaseModel):
    local_network: IPv4Network
    local_address: str
    real_ip: str
    listen_port: int
    private_key: str
    public_key: str
    clients: List[WgClientConfig]

    class Config:
        json_encoders = {
            IPv4Network: lambda v: str(v),
        }
        json_decoders = {
            IPv4Network: lambda v: IPv4Network(v),
        }

    def create_new_client(self, name: str, allowed_ips: str = "0.0.0.0/0",
                          persistent_keepalive: int = 20) -> WgClientConfig:
        client_private_key, client_public_key = WireGuardController.generate_keys()

        used_addresses = [client.local_address for client in self.clients]
        used_addresses.append(self.local_address)
        try:
            client_address = str(next(h for h in self.local_network.hosts() if str(h) not in used_addresses))
        except StopIteration:
            raise RuntimeError("No free address in network")

        client = WgClientConfig(
            name=name,
            local_address=client_address,
            private_key=client_private_key,
            public_key=client_public_key,
            allowed_ips=allowed_ips,
            persistent_keepalive=persistent_keepalive,
        )
        self.clients.append(client)
        return client

    def generate_config(self) -> str:
        interface_config = f"""[Interface]
Address = {self.local_address}/{self.local_network.prefixlen}
PrivateKey = {self.private_key}
ListenPort = {self.listen_port}"""

        peer_config = "\n\n".join([
            f"""[Peer]
PublicKey = {client.public_key}
AllowedIPs = {client.local_address}/32""" for client in self.clients
        ])

        return "\n\n".join([interface_config, peer_config])

    def generate_client_configs(self) -> Dict[str, str]:
        result = {}
        for client in self.clients:
            result[client.name] = f"""[Interface]
PrivateKey = {client.private_key}
Address = {client.local_address}/{self.local_network.prefixlen}
DNS = {DEFAULT_DNS}

[Peer]
PublicKey = {self.public_key}
AllowedIPs = {client.allowed_ips}
Endpoint = {self.real_ip}:{self.listen_port}
PersistentKeepalive = {client.persistent_keepalive}"""

        return result


def new_server_config() -> WgServerConfig:
    local_network = IPv4Network(DEFAULT_NETWORK)
    server_private_key, server_public_key = WireGuardController.generate_keys()
    external_ip = urllib.request.urlopen("https://api.ipify.org").read().decode("utf-8")
    return WgServerConfig(
        local_network=local_network,
        local_address=str(next(local_network.hosts())),
        real_ip=external_ip,
        listen_port=35053,
        private_key=server_private_key,
        public_key=server_public_key,
        clients=[],
    )


def load_config(path=DEFAULT_CONFIG_PATH, or_create=True):
    try:
        with open(path) as f:
            json_config = json.load(f)
            server_config = WgServerConfig(**json_config)
    except FileNotFoundError:
        if not or_create:
            raise
        server_config = new_server_config()
        with open(path, "w") as f:
            f.write(server_config.json())
    return server_config


def save_config(server_config, path=DEFAULT_CONFIG_PATH):
    with open(path, "w") as f:
        f.write(server_config.json())


def save_server_config(server_config: WgServerConfig, path=DEFAULT_WG_CONFIG_PATH):
    with open(path, "w") as f:
        f.write(server_config.generate_config())


def save_clients_config(server_config: WgServerConfig, path=DEFAULT_WG_CLIENTS_PATH):
    client_configs = server_config.generate_client_configs()
    for client_name, client_config in client_configs.items():
        with open(f"{path}/{client_name}.conf", "w") as f:
            f.write(client_config)
