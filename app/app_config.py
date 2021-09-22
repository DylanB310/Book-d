import os

CLIENT_ID = "0faf51c7-3f3d-4904-acc3-b158ed7c89de" # Application (client) ID of app registration

CLIENT_SECRET = "7_x_HcsLbpnVkZp13q68f7-1Ax7~eT_v4t" # Placeholder - for use ONLY during testing.
# In a production app, we recommend you use a more secure method of storing your secret,
# like Azure Key Vault. Or, use an environment variable as described in Flask's documentation:
# https://flask.palletsprojects.com/en/1.1.x/config/#configuring-from-environment-variables
# CLIENT_SECRET = os.getenv("CLIENT_SECRET")
# if not CLIENT_SECRET:
#     raise ValueError("Need to define CLIENT_SECRET environment variable")

AUTHORITY = "https://login.microsoftonline.com/common"  # For multi-tenant app
# AUTHORITY = "https://login.microsoftonline.com/f518c329-fab3-4e01-a05e-548f4a351002"

REDIRECT_PATH = "/getAToken"  # Used for forming an absolute URL to your redirect URI.
                              # The absolute URL must match the redirect URI you set
                              # in the app's registration in the Azure portal.

# You can find more Microsoft Graph API endpoints from Graph Explorer
# https://developer.microsoft.com/en-us/graph/graph-explorer
ENDPOINT = 'https://graph.microsoft.com/v1.0/users'  # This resource requires no admin consent

# You can find the proper permission names from this document
# https://docs.microsoft.com/en-us/graph/permissions-reference
SCOPE = ["User.ReadBasic.All"]

SESSION_TYPE = "filesystem"  # Specifies the token cache should be stored in server-side session

AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=bookdmedia;AccountKey=JJ3Uf/b6KjT9KFS9IC047O/2YJoNeRqbhnhqem6TiN/nfcrbuoFOH0vXGV0mODDhtEA/ipUwEiO+jJx/q3ABSw==;EndpointSuffix=core.windows.net"
