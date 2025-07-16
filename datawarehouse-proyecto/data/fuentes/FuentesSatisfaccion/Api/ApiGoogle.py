import requests
import pandas as pd
from datetime import datetime

# Tu API KEY de Google Maps
API_KEY = 'AIzaSyDzG216f56Sm79oTUAvoc6mOZgjWe2B-A4'

# Coordenadas del hotel
lat, lng = -8.1108722, -79.0289847

# 1. Buscar lugar más cercano del tipo "alojamiento"
nearby_url = (
    f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    f"?location={lat},{lng}&radius=50&type=lodging&key={API_KEY}"
)

try:
    response = requests.get(nearby_url)
    data = response.json()
    hotel = data.get("results", [])[0]
except (IndexError, KeyError):
    print(" No se encontraron hoteles cerca de las coordenadas dadas.")
    exit()

# 2. Datos básicos del hotel
place_id = hotel.get("place_id", "")
nombre = hotel.get("name", "N/A")
direccion = hotel.get("vicinity", "N/A")
rating_general = hotel.get("rating", "N/A")

print(f"\n Nombre: {nombre}")
print(f" Dirección: {direccion}")
print(f" Rating General: {rating_general}")
print(f" Place ID: {place_id}")

# 3. Obtener detalles del lugar con reseñas
details_url = (
    f"https://maps.googleapis.com/maps/api/place/details/json"
    f"?place_id={place_id}&fields=name,rating,reviews&key={API_KEY}"
)

details_response = requests.get(details_url)
details_data = details_response.json()
reviews = details_data.get("result", {}).get("reviews", [])

# 4. Procesar reseñas
datos = []
for i, r in enumerate(reviews):
    fecha = datetime.fromtimestamp(r.get("time")).strftime('%Y-%m-%d %H:%M:%S')
    datos.append({
        "ID": i + 1,
        "Puntaje": r.get("rating", ""),
        "Autor": r.get("author_name", ""),
        "Fecha": fecha,
        "Texto": r.get("text", "").strip()
    })

# 5. Mostrar por consola y guardar
if datos:
    df = pd.DataFrame(datos)
    print("\n Reseñas obtenidas:")
    print(df.to_string(index=False))  # Mostrar bien en consola

    df.to_excel("reseñas_por_coordenadas.xlsx", index=False)
    print("\n Archivo 'ApiGoogle.xlsx' guardado con éxito.")
else:
    print(" No hay reseñas disponibles para este lugar.")
