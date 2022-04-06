import json

from wg.config import WgServerConfig, new_server_config

DEFAULT_CONFIG_PATH = "config.json"


def load_config(path=DEFAULT_CONFIG_PATH):
    try:
        with open(path) as f:
            json_config = json.load(f)
            server_config = WgServerConfig(**json_config)
    except FileNotFoundError:
        server_config = new_server_config()
        with open(path, "w") as f:
            f.write(server_config.json())
    return server_config


if __name__ == "__main__":
    config = load_config()
    print(config)
    config.create_new_client("maxim_iphone")
    print(config.generate_config())
    print("\n\n\n")
    for config in config.generate_client_configs():
        print(config)
