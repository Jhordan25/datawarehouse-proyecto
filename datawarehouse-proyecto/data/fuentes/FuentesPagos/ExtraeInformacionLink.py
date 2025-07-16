from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import re

# === Función para obtener nombre limpio desde la URL ===
def formatear_entidad(url):
    match = re.search(r'/beneficios/([^/]+)/?', url)
    if match:
        nombre = match.group(1).replace('-', ' ').upper()
        if 'OFF' in nombre:
            nombre = nombre.replace('OFF', '% OFF')
        return nombre
    return "SIN ENTIDAD"

# === Función para extraer solo frases clave ===
def extraer_descripcion_relevante(driver):
    try:
        parrafos = driver.find_elements(By.TAG_NAME, 'p')
        textos = [p.text for p in parrafos if p.text.strip() != ""]

        frases_clave = []
        for texto in textos:
            texto_lower = texto.lower()
            if any(palabra in texto_lower for palabra in ['%', 'cuotas', 'intereses', 'código', 'válido', 'descuento', 'tarjeta']):
                frases_clave.append(texto)

        # Si no se encontró ninguna frase clave, devolver el primer párrafo
        return "\n".join(frases_clave) if frases_clave else textos[0] if textos else "Sin texto"
    except:
        return "Sin descripción relevante"

# === Leer archivo con enlaces ===
df = pd.read_excel("beneficios.xlsx")  # Asegúrate que este archivo esté en la misma carpeta

# === Configurar Selenium ===
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# === Procesar cada URL ===
titulos = []
descripciones = []
urls = []

for index, row in df.iterrows():
    url = row["Enlace"]
    driver.get(url)
    time.sleep(2)

    entidad = formatear_entidad(url)
    descripcion = extraer_descripcion_relevante(driver)

    titulos.append(entidad)
    descripciones.append(descripcion)
    urls.append(url)

    print(f"[✓] {entidad} procesado")

# === Guardar en nuevo Excel ===
df_resumen = pd.DataFrame({
    "Entidad / Título": titulos,
    "Descripción Resumida": descripciones,
    "Enlace": urls
})

df_resumen.to_excel("beneficios_Actualizados3.xlsx", index=False)
print("\n✅ Archivo 'beneficios_resumidos.xlsx' generado con éxito.")

driver.quit()   



