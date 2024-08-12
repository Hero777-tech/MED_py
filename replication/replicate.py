#ip and other replication verical
# import requests

# def replicate_to_servers(filepath):
#     servers = ['http://server1.com/upload', 'http://server2.com/upload']
#     for server_url in servers:
#         with open(filepath, 'rb') as file_data:
#             response = requests.post(server_url, files={'file': file_data})
#             if response.status_code == 200:
#                 print(f'File successfully replicated to {server_url}')
#             else:
#                 print(f'Failed to replicate file to {server_url}')


#server port one ip ip/n n--> multiple ports 5000 50022 50021 etc

import requests

def replicate_to_servers(filepath):
    # List of local server instances (ports) to replicate to
    servers = ['http://127.0.0.1:5001/upload', 'http://127.0.0.1:5002/upload']
    for server_url in servers:
        with open(filepath, 'rb') as file_data:
            response = requests.post(server_url, files={'file': file_data})
            if response.status_code == 200:
                print(f'File successfully replicated to {server_url}')
            else:
                print(f'Failed to replicate file to {server_url}')
