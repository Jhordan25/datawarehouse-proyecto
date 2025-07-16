import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc

print("🔄 Abriendo navegador...")
options = uc.ChromeOptions()
options.add_argument("--start-maximized")
driver = uc.Chrome(options=options)

# Abrir búsqueda en Airbnb
url = "https://www.airbnb.com.pe/s/Tumbes--Peru/homes?adults=2&checkin=2025-07-14&checkout=2025-07-15"
driver.get(url)
print("⌛ Esperando que cargue la página...")
time.sleep(12)

# Hacer scroll para cargar más resultados
print("🔃 Haciendo scroll para cargar más resultados...")
body = driver.find_element(By.TAG_NAME, "body")
for _ in range(10):
    body.send_keys(Keys.END)
    time.sleep(3)

print("🔍 Extrayendo datos de alojamientos...")

alojamientos = driver.find_elements(By.XPATH, '//div[@itemprop="itemListElement"]')

data = []

for alojamiento in alojamientos:
    try:
        nombre = alojamiento.find_element(By.XPATH, './/meta[@itemprop="name"]').get_attribute("content")
    except:
        nombre = ""

    try:
        precio = alojamiento.find_element(By.XPATH, './/span[contains(text(), "S/")]').text
    except:
        precio = "N/A"

    try:
        ubicacion = alojamiento.find_element(By.XPATH, './/span[contains(text(), "Tumbes")]').text
    except:
        ubicacion = "Tumbes, Perú"

    try:
        puntuacion = alojamiento.find_element(By.XPATH, './/span[contains(@aria-label, "puntuación")]').get_attribute("aria-label")
    except:
        puntuacion = "No reviews"

    try:
        url = alojamiento.find_element(By.TAG_NAME, "a").get_attribute("href")
    except:
        url = "N/A"

    print(f"🧩 Extraído → Nombre: {nombre} | Precio: {precio} | Ubicación: {ubicacion} | Puntuación: {puntuacion}")

    data.append({
        "Nombre": nombre,
        "Precio": precio,
        "Ubicación": ubicacion,
        "Puntuación": puntuacion,
        "URL": url
    })

# Guardar en Excel
df = pd.DataFrame(data)
df.to_excel("Alojamientos_Airbnb_Tumbes.xlsx", index=False)
print("✅ Datos guardados en 'Alojamientos_Airbnb_Tumbes.xlsx'")

# Cierre limpio
try:
    driver.quit()
except:
    pass












