from wg.config import load_config, save_config, save_server_config, save_clients_config

if __name__ == "__main__":
    server_config_obj = load_config()
    client_name = input("Enter client name: ")
    server_config_obj.create_new_client(client_name)
    save_config(server_config_obj)
    save_server_config(server_config_obj)
    save_clients_config(server_config_obj)
