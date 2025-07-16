import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests

# CONFIGURAR OPCIONES DEL NAVEGADOR
options = uc.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")

driver = uc.Chrome(options=options)

try:
    driver.get("https://exportcomments.com/")
    wait = WebDriverWait(driver, 60)

    print("🔄 Cargando página...")

    # Ingresar URL del video
    input_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']")))
    input_box.send_keys("https://www.facebook.com/HotelesCostadelSolPeru/posts/pfbid02NmBnjzKXbB3kRHppkvapBPUadarMSVFU4bvDzqrzsj7Bog2NiahSWE3foojfWdf4l")

    submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit_button.click()

    print("⏳ Esperando procesamiento...")

    # Esperar a que aparezca el botón verde de dropdown
    dropdown_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'dropdown-toggle') and contains(., 'Download facebook comments')]"))
    )
    dropdown_button.click()
    print("✅ Botón de descarga desplegable clickeado.")

    # Esperar el link "Save as Excel File" dentro del menú desplegable
    excel_link = wait.until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(., 'Save as Excel File')]"))
    )
    file_url = excel_link.get_attribute("href")
    print("📥 Enlace de descarga Excel:", file_url)

    # Descargar el archivo
    response = requests.get(file_url)
    with open("comentarios_Facebook.xlsx", "wb") as f:
        f.write(response.content)

    print("✅ Archivo descargado correctamente.")

    time.sleep(3)

finally:
    driver.quit()
    print("🚪 Navegador cerrado.")
