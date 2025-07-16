
# Instalar pandas si no está instalado

import pandas as pd

# Cargar el archivo .txt (asegúrate de subirlo primero al entorno de Colab)
from google.colab import files
uploaded = files.upload()  # Te pedirá que subas el archivo .txt

# Leer el archivo .txt
with open(next(iter(uploaded)), "r", encoding="utf-8") as f:
    lineas = f.readlines()

# Procesar datos: dividir en número y tendencia
data = []
for linea in lineas:
    if ")" in linea:
        num, texto = linea.strip().split(")", 1)
        data.append((int(num.strip()), texto.strip()))

# Crear DataFrame
df = pd.DataFrame(data, columns=["N°", "Tendencia"])

# Guardar a Excel
nombre_excel = "tendencias_fidelizacion.xlsx"
df.to_excel(nombre_excel, index=False)

# Descargar el Excel generado
files.download(nombre_excel)