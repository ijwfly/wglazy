from wg.config import load_config, save_config

if __name__ == "__main__":
    server_config_obj = load_config()
    print(server_config_obj.generate_config())
    save_config(server_config_obj)
