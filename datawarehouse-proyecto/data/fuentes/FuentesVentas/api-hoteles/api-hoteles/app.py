from flask import Flask, render_template
import requests

app = Flask(__name__)

API_KEY = "7731c99f90msh48f43c866dc8b03p1079b0jsn9402365c7e45"
HEADERS = {
    "x-rapidapi-host": "hotels4.p.rapidapi.com",
    "x-rapidapi-key": API_KEY,
    "content-type": "application/json"
}

CIUDADES_PERU = ["Trujillo", "Piura", "Cusco", "Arequipa", "Tumbes"]

@app.route("/")
def index():
    hoteles = []

    for ciudad in CIUDADES_PERU:
        try:
            # Buscar regionId
            search_url = "https://hotels4.p.rapidapi.com/locations/v3/search"
            search_params = {"q": ciudad, "locale": "en_US"}
            res = requests.get(search_url, headers=HEADERS, params=search_params)
            data = res.json()

            region_id = ""
            for lugar in data.get("sr", []):
                if "gaiaId" in lugar:
                    region_id = lugar["gaiaId"]
                    break

            if not region_id:
                continue

            # Buscar hoteles con ese regionId
            hotel_url = "https://hotels4.p.rapidapi.com/properties/v2/list"
            payload = {
                "currency": "USD",
                "eapid": 1,
                "locale": "en_US",
                "siteId": 300000001,
                "destination": {"regionId": region_id},
                "checkInDate": {"day": 1, "month": 8, "year": 2025},
                "checkOutDate": {"day": 2, "month": 8, "year": 2025},
                "rooms": [{"adults": 2}],
                "resultsSize": 50,
                "sort": "PRICE_LOW_TO_HIGH"
            }

            res = requests.post(hotel_url, headers=HEADERS, json=payload)
            hoteles_data = res.json().get("data", {}).get("propertySearch", {}).get("properties", [])

            for hotel in hoteles_data:
                nombre = hotel.get("name", "Sin nombre")
                ubicacion = hotel.get("neighborhood", {}).get("name", "Ubicación no disponible")
                precio = hotel.get("price", {}).get("displayMessages", [{}])[0].get("lineItems", [{}])[0].get("price", {}).get("formatted", "USD -")
                hoteles.append({"ciudad": ciudad, "nombre": nombre, "ubicacion": ubicacion, "precio": precio})

        except Exception as e:
            print(f"Error en {ciudad}: {e}")

    return render_template("index.html", hoteles=hoteles)

if __name__ == "__main__":
    app.run(debug=True)



























