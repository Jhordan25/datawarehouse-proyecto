import os
from PIL import Image
import pytesseract
import pandas as pd
from pdf2image import convert_from_path

# Configuración
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"
poppler_path = r"C:\poppler\Library\bin"  # <-- AJUSTA ESTA RUTA

# Convertir PDF a imágenes
ruta_pdf = r"C:\Users\user\Desktop\FuentesBigData\tabla.pdf"
paginas = convert_from_path(ruta_pdf, dpi=300, poppler_path=poppler_path)

# OCR en todas las páginas (puedes limitar si es largo)
texto_crudo = ""
for pagina in paginas:
    texto_crudo += pytesseract.image_to_string(pagina, lang='spa') + "\n"

# Limpieza de texto
lineas = [linea.strip() for linea in texto_crudo.split('\n') if linea.strip().isdigit() or linea.strip().isalpha() or linea.strip().replace('*', '').isalnum()]

# Categorías
categorias = [
    "5 ESTRELLAS", "4 ESTRELLAS", "3 ESTRELLAS", "2 ESTRELLAS", "1 ESTRELLA",
    "ALBERGUE", "ECOLODGE"
]

# Extraer datos por bloques
datos = []
i = 0
while i < len(lineas):
    if lineas[i].isdigit() and 2000 <= int(lineas[i]) <= 2030:
        año = int(lineas[i])
        valores = []
        for j in range(1, 8):
            if i + j < len(lineas) and lineas[i + j].isdigit():
                valores.append(int(lineas[i + j]))
            else:
                valores.append(None)
        if len(valores) == 7:
            datos.append([año] + valores)
        i += 8
    else:
        i += 1

# Crear DataFrame
filas = []
id_counter = 1
for bloque in datos:
    año = bloque[0]
    for cat, valor in zip(categorias, bloque[1:]):
        filas.append({
            "ID": id_counter,
            "Año": año,
            "Categoría": cat,
            "Valor": valor
        })
        id_counter += 1

df = pd.DataFrame(filas)

# Guardar resultado
df.to_excel("resultado_desde_pdf.xlsx", index=False)

print("✅ Proceso completado. Archivo 'resultado_desde_pdf.xlsx' generado.")
