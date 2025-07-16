import requests

ACCESS_TOKEN = "pATCNRSoWxD7nN6PhWysxnWlshGD"

url = "https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city"
params = {
    "cityCode": "TRU",  # Código IATA de Trujillo
    "radius": 50,
    "radiusUnit": "KM"
}
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

response = requests.get(url, headers=headers, params=params)
data = response.json()

hoteles = data.get("data", [])
print(f"🏨 Hoteles registrados por Amadeus en Trujillo: {len(hoteles)}")
for hotel in hoteles:
    print(f"- {hotel['name']} (ID: {hotel['hotelId']})")






