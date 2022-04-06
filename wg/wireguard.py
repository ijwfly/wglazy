import subprocess


class WireGuardController:
    def __init__(self, config_path: str):
        self.config_path = config_path

    @staticmethod
    def generate_keys():
        private_key = subprocess.run(["wg", "genkey"], capture_output=True, check=True).stdout.decode("utf-8").strip()
        public_key = subprocess.run(["wg", "pubkey"], input=private_key.encode(), capture_output=True, check=True).stdout.decode("utf-8").strip()
        return private_key, public_key
