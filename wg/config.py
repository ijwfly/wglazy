import urllib.request
from typing import List

from ipaddress import IPv4Network
from pydantic import BaseModel

from wg.wireguard import WireGuardController

DEFAULT_NETWORK = "10.8.0.0/24"
DEFAULT_DNS = "1.1.1.1"


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
AllowedIPs = {client.local_address}/{self.local_network.prefixlen}""" for client in self.clients
        ])

        return "\n\n".join([interface_config, peer_config])

    def generate_client_configs(self) -> List[str]:
        result = []
        for client in self.clients:
            result.append(f"""
[Interface]
Address = {client.local_address}/{self.local_network.prefixlen}
PrivateKey = {client.private_key}
DNS = {DEFAULT_DNS}

[Peer]
PublicKey = {self.public_key}
AllowedsIPs = {client.allowed_ips}
Endpoint = {self.real_ip}:{self.listen_port}
PersistentKeepalive = {client.persistent_keepalive}""")
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
