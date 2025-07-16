import requests

client_id = "tmMHaYlIyEkEILga2pS6X52ZOms1eL6P"
client_secret = "NwTa88kKG7GT3Klz"

# URL para autenticación
auth_url = "https://test.api.amadeus.com/v1/security/oauth2/token"

# Payload
data = {
    "grant_type": "client_credentials",
    "client_id": client_id,
    "client_secret": client_secret
}

# Hacer POST para obtener token
response = requests.post(auth_url, data=data)
if response.status_code == 200:
    token = response.json().get("access_token")
    print("✅ Token de acceso:", token)
else:
    print("❌ Error al obtener token:", response.text)
