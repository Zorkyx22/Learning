import os
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

keyVaultName = os.environ["KEY_VAULT_NAME"]
keyVaultURI = f"https://{keyVaultName}.vault.azure.net"

azureCreds = DefaultAzureCredential()
keyVaultClient = SecretClient(vault_url=keyVaultURI, credential=azureCreds)

credentials = {
    "username": keyVaultClient.get_secret("username"),
    "password": keyVaultClient.get_secret("password"),
    }
api_key = keyVaultClient.get_secret("api_key")

def authenticate_somewhere(credentials, api_key):
    pass