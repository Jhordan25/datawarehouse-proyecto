import pandas as pd
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Configuración del navegador
options = uc.ChromeOptions()
options.add_argument("--start-maximized")
driver = uc.Chrome(options=options)

print("🔄 Abriendo navegador y cargando Booking...")

# URL de búsqueda para hoteles en Tumbes, Perú
url = "https://www.booking.com/searchresults.es.html?ss=Tumbes%2C+Per%C3%BA&checkin=2025-07-16&checkout=2025-07-17&group_adults=2&no_rooms=1&group_children=0"
driver.get(url)

time.sleep(8)  # Espera para que cargue todo

# Hacer scroll hacia abajo para asegurar carga dinámica
for _ in range(3):
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
    time.sleep(2)

print("🔍 Buscando tarjetas de hotel...")

# Captura de las tarjetas de hotel
hoteles = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="property-card"]')
print(f"✅ Se detectaron {len(hoteles)} hoteles.")

data = []

for i, hotel in enumerate(hoteles, 1):
    try:
        nombre = hotel.find_element(By.CSS_SELECTOR, 'div[data-testid="title"]').text.strip()
    except:
        nombre = ""

    try:
        ubicacion = hotel.find_element(By.CSS_SELECTOR, 'span[data-testid="address"]').text.strip()
    except:
        ubicacion = ""

    try:
        precio = hotel.find_element(By.CSS_SELECTOR, 'span[data-testid="price-and-discounted-price"]').text.strip()
    except:
        try:
            precio = hotel.find_element(By.CSS_SELECTOR, 'span[data-testid="price-and-discounted-price"] span').text.strip()
        except:
            precio = ""

    try:
        enlace = hotel.find_element(By.TAG_NAME, 'a').get_attribute("href")
    except:
        enlace = ""

    print(f"{i}. 🏨 {nombre} | 💲 {precio} | 📍 {ubicacion}")

    data.append({
        "ID": i,
        "Nombre": nombre,
        "Precio": precio,
        "Ubicación": ubicacion,
        "URL": enlace
    })

driver.quit()

# Guardar en Excel
df = pd.DataFrame(data)
df.to_excel("Hoteles_Booking_Tumbes_Completo.xlsx", index=False)
print(f"\n✅ {len(data)} hoteles guardados en 'Hoteles_Booking_Tumbes_Completo.xlsx'")














