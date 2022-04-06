from wg.config import load_config, save_config, save_server_config, save_clients_config

if __name__ == "__main__":
    server_config_obj = load_config()
    print(server_config_obj)
    client_name = input("Enter client name: ")
    server_config_obj.create_new_client(client_name)
    print(server_config_obj.generate_config())
    print("\n\n")
    for client_name, client_config in server_config_obj.generate_client_configs().items():
        print('-------------')
        print(client_name)
        print(client_config)

    save_config(server_config_obj)

    save_server_config(server_config_obj)
    save_clients_config(server_config_obj)
