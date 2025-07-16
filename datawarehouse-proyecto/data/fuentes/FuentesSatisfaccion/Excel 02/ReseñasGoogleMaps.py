from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd

# Configurar navegador
options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # Actívalo si no deseas ver el navegador
options.add_argument("--lang=es")
options.add_argument("--start-maximized")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# URL del hotel en Google Maps
url = "https://www.google.com/maps/place/Hotel+Costa+del+Sol+Trujillo+Centro/@-8.1108669,-79.0315596,16z/data=!4m11!3m10!1s0x91ad3d837dae4849:0xeb74ec7b04e11297!5m2!4m1!1i2!8m2!3d-8.1108722!4d-79.0289847!9m1!1b1!16s%2Fg%2F1tfk5hnd?entry=ttu"
driver.get(url)
time.sleep(5)

# Abrir reseñas
try:
    boton = driver.find_element(By.XPATH, "//button[contains(., 'reseñas')]")
    boton.click()
    time.sleep(5)
except:
    print("No se pudo abrir reseñas.")
    driver.quit()
    exit()

# Scroll para cargar más reseñas
scroll_div = driver.find_element(By.XPATH, '//div[@role="region"]')
for _ in range(15):
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_div)
    time.sleep(1.5)

# Expandir textos truncados
time.sleep(2)
mas_botones = driver.find_elements(By.XPATH, '//button[contains(text(), "Más")]')
for btn in mas_botones:
    try:
        driver.execute_script("arguments[0].click();", btn)
        time.sleep(0.2)
    except:
        continue

# Extraer solo textos de reseñas
reseñas = driver.find_elements(By.CLASS_NAME, "jftiEf")
datos = []

for i, r in enumerate(reseñas[:100]):
    try:
        texto = r.find_element(By.CLASS_NAME, "wiI7pd").text.strip()
    except:
        texto = ""

    print(f"\n📌 Reseña #{i+1}")
    print(f"📝 Texto: {texto[:300]}{'...' if len(texto) > 300 else ''}")

    datos.append({
        "ID": i + 1,
        "Reseña": texto
    })

# Guardar en Excel
df = pd.DataFrame(datos)
df.to_excel("reseñas_googlemaps_solo_texto.xlsx", index=False)
print(f"\n✅ {len(datos)} reseñas guardadas en 'ReseñasGoogleMaps.xlsx'.")

driver.quit()
