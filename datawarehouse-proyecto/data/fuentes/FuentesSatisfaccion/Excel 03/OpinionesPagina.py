import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Función para extraer opiniones de una sola página
def extraer_opiniones(url, offset_id=0):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')

    opiniones = []
    bloques = soup.select("div.tmb-post")

    for i, bloque in enumerate(bloques, 1):
        titulo = bloque.select_one("h3.t-entry-title a")
        texto = bloque.select_one("div.t-entry > p")

        opiniones.append({
            "ID": offset_id + i,
            "Titulo": titulo.get_text(strip=True) if titulo else "",
            "Texto": texto.get_text(strip=True) if texto else "",
            "URL": titulo["href"] if titulo else ""
        })

    return opiniones

# Scrapeamos múltiples páginas
data_total = []

base_url = "https://www.costadelsolperu.com/opinion/page/"
paginas = 8  # Puedes ajustar este número si hay más páginas

current_id = 0
for num in range(1, paginas + 1):
    url = base_url + str(num) if num > 1 else "https://www.costadelsolperu.com/opinion/"
    print(f"📄 Procesando página {num}...")
    try:
        opiniones = extraer_opiniones(url, offset_id=current_id)
        data_total.extend(opiniones)
        current_id += len(opiniones)
        time.sleep(1.5)  # Pausa para evitar bloqueos
    except Exception as e:
        print(f"❌ Error en página {num}: {e}")

# Guardamos en Excel
df = pd.DataFrame(data_total)
df.to_excel("opiniones_costa_del_sol.xlsx", index=False)
print(f"\n✅ Total de opiniones guardadas: {len(df)} en 'OpinionesPagina.xlsx'")

