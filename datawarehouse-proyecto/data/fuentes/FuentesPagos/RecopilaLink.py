from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import pandas as pd

# Configurar Selenium
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://www.costadelsolperu.com/beneficios/")
time.sleep(3)  # Esperar a que cargue el contenido dinámico

# Obtener el contenido de la página
page_source = driver.page_source
soup = BeautifulSoup(page_source, 'html.parser')

# Encontrar los elementos que contienen los beneficios (enlaces)
benefits = soup.find_all('a', href=lambda href: href and '/beneficios/' in href)

# Preparar datos para el DataFrame
data = []
print("Lista de beneficios encontrados:")
for benefit in benefits:
    benefit_text = benefit.text.strip()
    benefit_link = benefit.get('href')
    if not benefit_link.startswith('http'):
        benefit_link = 'https://www.costadelsolperu.com' + benefit_link
    if benefit_text and "Ver Beneficio" not in benefit_text:
        print(f"Beneficio: {benefit_text} | Enlace: {benefit_link}")
        data.append([benefit_text, benefit_link])

# Crear DataFrame y guardar en Excel
df = pd.DataFrame(data, columns=["Beneficio", "Enlace"])
df.to_excel("beneficios.xlsx", index=False)
print("Resultados guardados en beneficios.xlsx")

# Cerrar el navegador
driver.quit()



