
import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from google.colab import files

# Paso 1: Obtener contenido en inglés
url = "https://blog.propellocloud.com/customer-loyalty-trends"
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

# Paso 2: Extraer títulos de tendencias (en h3)
tendencias_raw = soup.find_all("h3")
tendencias_ingles = [t.get_text(strip=True) for t in tendencias_raw if any(str(n) in t.get_text() for n in range(1, 13))]

# Paso 3: Traducir al español
traductor = GoogleTranslator(source='en', target='es')
tendencias_espanol = [traductor.translate(t) for t in tendencias_ingles]

# Paso 4: Guardar en archivo
filename = "tendencias_fidelizacion.txt"
with open(filename, "w", encoding="utf-8") as f:
    for i, t in enumerate(tendencias_espanol, 1):
        f.write(f"{i}) {t}\n")

# Paso 5: Descargar
files.download(filename)