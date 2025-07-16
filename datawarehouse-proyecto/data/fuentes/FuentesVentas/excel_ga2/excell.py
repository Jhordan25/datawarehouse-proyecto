import time
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Abre navegador
print("🔄 Abriendo navegador...")
options = uc.ChromeOptions()
options.add_argument("--start-maximized")
driver = uc.Chrome(options=options)

try:
    url = "https://www.hotelscombined.com/hotels/Tumbes,Peru-p178182/2025-07-13/2025-07-14/2adults;map?ucs=1ds94fi&sort=distance_a"
    driver.get(url)

    print("⌛ Esperando que cargue la página...")
    wait = WebDriverWait(driver, 20)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".yuAt")))

    print("🔃 Haciendo scroll para cargar más hoteles...")
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_tries = 0
    while scroll_tries < 15:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            scroll_tries += 1
        else:
            scroll_tries = 0
        last_height = new_height

    print("🔍 Extrayendo datos de hoteles...")
    hoteles = driver.find_elements(By.CSS_SELECTOR, ".yuAt")
    data = []

    for hotel in hoteles:
        try:
            nombre_elem = hotel.find_element(By.CSS_SELECTOR, ".c9Hnq-hotel-name a")
            nombre = nombre_elem.text.strip()
            url_hotel = "https://www.hotelscombined.com" + nombre_elem.get_attribute("href")
        except:
            nombre = ""
            url_hotel = ""

        try:
            precio = hotel.find_element(By.CSS_SELECTOR, ".Ptt7-price").text.strip()
        except:
            precio = ""

        try:
            ubicacion = hotel.find_element(By.CSS_SELECTOR, ".upS4-landmark-text").text.strip()
        except:
            ubicacion = ""

        try:
            puntuacion_num = hotel.find_element(By.CSS_SELECTOR, ".Dp6Q").text.strip()
        except:
            puntuacion_num = ""

        try:
            puntuacion_texto = hotel.find_element(By.CSS_SELECTOR, ".AFFP-des").text.strip()
        except:
            puntuacion_texto = ""

        if nombre or precio or ubicacion:
            print(f"🧩 Extraído → Nombre: {nombre} | Precio: {precio} | Ubicación: {ubicacion} | Puntuación: {puntuacion_num} {puntuacion_texto}")
            data.append({
                "Nombre": nombre,
                "Precio": precio,
                "Ubicación": ubicacion,
                "Puntuación": puntuacion_num,
                "Opiniones": puntuacion_texto,
                "URL": url_hotel
            })

    if data:
        df = pd.DataFrame(data)
        df.to_excel("Hoteles_HotelsCombined_Tumbes.xlsx", index=False)
        print("✅ Datos guardados en 'Hoteles_HotelsCombined_Tumbes.xlsx'")
    else:
        print("⚠️ No se extrajo ningún hotel con datos válidos.")

finally:
    driver.quit()




























