import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup
import re  # Para limpiar caracteres

# Función para limpiar texto: solo letras, tildes, ñ y espacios
def limpiar_texto(texto):
    if texto:
        texto = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]', '', texto)
        return texto.strip()
    return ""

# Configuración del navegador
options = Options()
options.add_argument("--headless")
options.add_argument("--window-size=1920,1080")
options.add_argument("--lang=es")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 1. Abrir página general
base_url = "https://www.atrapalo.pe/hoteles/america/peru/tumbes/tumbes/"
driver.get(base_url)
time.sleep(6)

# Hacer scroll para asegurar que cargue todo
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(4)

# Extraer toda la estructura HTML
soup = BeautifulSoup(driver.page_source, 'lxml')

# Bloques completos de hoteles
bloques = soup.select("div.ranking__list-item.clearfix")

data = []
for i, bloque in enumerate(bloques, 1):
    try:
        nombre = limpiar_texto(bloque.select_one("a.ranking__list-name").get_text(strip=True))
    except:
        nombre = ""

    try:
        puntaje = bloque.select_one("span.opi-rating").get_text(strip=True)
    except:
        puntaje = ""

    try:
        resumen = limpiar_texto(bloque.select_one("span.ranking__list-title").get_text(strip=True))
    except:
        resumen = ""

    try:
        link_tag = bloque.select_one("a.ranking__list-opinions")
        n_op = link_tag.get_text(strip=True)
        url_op = "https://www.atrapalo.pe" + link_tag["href"]
    except:
        url_op = ""
        n_op = ""

    try:
        descripcion = limpiar_texto(bloque.select_one("p.ranking__list-detail").get_text(strip=True))
    except:
        descripcion = ""

    try:
        direccion = limpiar_texto(bloque.select_one("p.ranking__list-info").get_text(strip=True))
    except:
        direccion = ""

    print(f"\n🏨 Hotel #{i}: {nombre}")
    print("⭐ Puntaje:", puntaje)
    print("📍 Dirección:", direccion)
    print("💬 Opiniones:", n_op)

    data.append({
        "ID": i,
        "Nombre": nombre,
        "Puntaje": puntaje,
        "Resumen": resumen,
        "TotalOpiniones": n_op,
        "Dirección": direccion,
        "Descripción": descripcion,
        "URL": url_op
    })

driver.quit()

# Guardar a Excel
df = pd.DataFrame(data)
df.to_excel("RankingHotelesTumbes.xlsx", index=False)
print(f"\n✅ {len(data)} hoteles guardados en 'RankingHotelesTumbes.xlsx'")

