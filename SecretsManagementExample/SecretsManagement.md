# Secrets Management
This is a very very simple example of how one could manage secrets in an application. I will show the different good and bad ways to do so by using python and Windows. The same can be applied to Linux, but using a different package manager for grabbing AZ CLI (Spoiler??) and by using `export` instead of `set`.

# The bad way
Hard-coding secrets. Bad way. Big Bad.
```python
credentials = {
        'username': 'marty88',
        'password': 'DeLoreanDMC-12',
    }
api_key = 'b85e5e7d-9b11-4d49-acd5-1e045f90da36'

def authenticate_somewhere(credentials, api_key):
    pass
```
This exposes your credentials to people that look at your code. That might feel secure, but you commit your code to source control, which means that it could be hacked or leaked. It also means that any disgruntled programmer can expose or distribute these credentials freely.

# One Way : Environment Variables
Environment variables are a way to bypass this issue. When deploying your code to a server or device, you can set it up so that your confidential information is already in the environment variables of the system before launching your application.
Environment variables are more secure since the secrets are hidden from plain view, they cannot be commited to source control. There are different levels of secure storage in environment variables:
1. Plaintext secrets stored in environment variables
2. Encrypted secrets stored in environment variables
3. Encrypted secrets injected in application process from HSM

And probably many more creative ways for secrets to be held by the server that runs your application. A problem one could face by using this technique is that the machines that the developpers use must also have a mechanism for storing and using secrets. We don't want them to hardcode the credentials!

There exists multiple secrets management utilities meant for development use that simulate the use of environment variables. This is what developpers should use to simulate their environment.

### Python
Under python you have `python-dotenv` that can be used like so:
#### ./.secrets
```
USERNAME=marty88
PASSWORD=DeLoreanDMC-12
API_KEY=b85e5e7d-9b11-4d49-acd5-1e045f90da36
```

#### ./main.py
```python
from dotenv import load_dotenv
import os

load_dotenv(".secrets")

credentials = {
    'username': os.getenv("USERNAME"),
    'password': os.getenv("PASSWORD"),
}
api_key = os.getenv('API_KEY')

def authenticate_somewhere(credentials, api_key):
    pass
```

### .NET
Under .NET you can use the built-in developper utility `user-secrets` either with a json file directly or via the command line.
#### ./secrets.json
```json
{

    "credentials:username":"marty88",
    "credentials:password":"DeLoreanDMC-12",
}
```

#### Command Line Utility
```bash
dotnet user-secrets set "api_key" "b85e5e7d-9b11-4d49-acd5-1e045f90da36"
```

#### ./main.cs
```cs
var builder = WebApplication.CreateBuilder(args)

var username = builder.Configuration["credentials:username"]
var password = builder.configuration["credentials:password"]
var api_ley = builder.configuraiton["api_key"]

private int Authenticate(string username, string password, string api_key) {
    return 0;
}
```

### C++
Under C++ there really are no utilities for it. (And, to be fair, C++ devs would probably not use them anyway) so you have to set your environment variables manually and use them in your code like so

#### Manually Setting your variables
```bash
set USERNAME=marty88
set PASSWORD=DeLoreanDMC-12
set API_KEY="b85e5e7d-9b11-4d49-acd5-1e045f90da36"
```

#### ./main.cpp
```cpp
#include <cstdlib>
#include <iostream>
const char* user = std::getenv("USERNAME");
const char* passw = std::getenv("PASSWORD");
const char* api_key = std::getenv("API_KEY");

int authenticate(char* username, char* password, char* api_key) {
    return 0;
}
```

## Another Way : Secrets Managers
There are many Secrets Managers that are used across the industry, mostly split among big Infrastructure providers such as Microsoft, Google. Other companies such as BitWarden also provide Secrets Managing solutions and there even exist Docker solutions such as Docker Secrets.

In this example, I'll show how you can use Microsoft's solution, Azure Key Vault, in a python scenario.

### Azure CLI and Azure Portal
Before doing anything, you need to have a valid Azure Subscription and rights to create resources in your organization. For the sake of this example, I'll be using my private account for which I have request a free trial.
You can access Azure through the Command Line Interface (CLI) or through the [web portal](azure.portal.com). I will focus on doing it through the [Azure Command Line Interface](https://learn.microsoft.com/en-us/cli/azure/).

*First, we have to install Azure CLI. Let's use Windows Pacakge Manager*
```bash
winget install -e --id Microsoft.AzureCLI
```

*Then, let's use it to log in*
```bash
az login --tenant "<redacted>"
```

*Which will prompt you to select your Azure subscription. Select it using the number associated with it (mine was '1' since I only have the one subscription). Next, we need to create a resource group in which we want to store our keyvault. __Don't forget to delete this group at the end if you are following along the example!!__*
```bash
az group create --name <your-group-name> --location <your-location>
```

*And then create our keyvault in that resource group*
```bash
az keyvault create --name <your-keyvault-name> --resource-group <your-group-name> --location <your-location>
```

*Note that your resource group and location should be the same across both of these commands. You keyvault now exists! We need to add stuff in it. Let's create the same three secrets we defined earlier:*
```bash
az keyvault secret set --vault-name <your-keyvault-name> --name "username" --value "marty88"
az keyvault secret set --vault-name <your-keyvault-name> --name "password" --value "DeLoreanDMC-12"
az keyvault secret set --vault-name <your-keyvault-name> --name "api_key" --value "b85e5e7d-9b11-4d49-acd5-1e045f90da36"
```

*Great! Now let's make sure they are in our vault:*
```bash
az keyvault secret list --vault-name <your-keyvault-name>
az keyvault secret show --vault-name <your-keyvault-name> --name "username"
az keyvault secret show --vault-name <your-keyvault-name> --name "password"
az keyvault secret show --vault-name <your-keyvault-name> --name "api_key"
```

*All secrets accounted for! Now all we need to do is to do use them in our applications. In order to facilitate the distinction between dev and prod environments, we'll set the keyvault name in our environment variables. Your application will need to be assigned a role in your Role-Based Access Control. Let's keep that for another article.*
#### Project Setup
```bash
pip install azure-identity azure-keyvault-secrets
set KEY_VAULT_NAME=<your-keyvault-name>
```

#### ./main.py
```python
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
```

As Microsoft says in their quickstart guide :
> `DefaultAzureCredential` authenticates to key vault using the credentials of the local development user logged into the Azure CLI. When the application is deployed to Azure, the same `DefaultAzureCredential` code can automatically discover and use a managed identity that is assigned to an App Service, Virtual Machine, or other services. For more information, see [Managed Identity Overview](https://learn.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/overview).

This means that, as a development user, we only have to use `az login` as shown earlier to login prior to running this program in our development environment. When deploying, you won't have to change this code, but you will have to assign a role for your application in your Azure environment.

Now, __if you followed along with the example__ you should __delete your resource group__. This will destroy the keyvault we created together and stop you from incurring unwanted charges to your account.

### Why is the secrets manager the best option in many cases?
Let's start out and say that the best secrets management strategy is the one that gets your team the best security. Maybe that's environment injection. Maybe that's Application Injection like with Azure Key Vault. All in all, you have to choose which one is best for you.

Secrets Managers are often the best solution because they handle really well different environments and rotating keys. However, in an embedded systems development context for instance, they can't really be used, so environment injection could be your best bet!


















