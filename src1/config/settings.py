import os

print(os.path.dirname(__file__), 'properties\client_secrets.json')
print(os.path.join(os.path.dirname(__file__), 'properties\client_secrets.json') )
CLIENT_SECRETS_FILE=os.path.join(os.path.dirname(__file__), 'properties\client_secrets.json') 