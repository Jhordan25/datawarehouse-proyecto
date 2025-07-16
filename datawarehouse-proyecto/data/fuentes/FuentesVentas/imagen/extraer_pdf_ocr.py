import pytesseract
from pdf2image import convert_from_path
import pandas as pd
import os
import cv2
from datetime import datetime
from pytesseract import Output

# Ruta a Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Ruta al PDF
PDF_PATH = r"C:\Users\Usuario\Desktop\carpeta\Doc3.pdf"

# Ruta a Poppler
POPLER_BIN_PATH = r"C:\Poppler\Library\bin"

# Carpeta de salida
OUTPUT_DIR = r"C:\Users\Usuario\Desktop\carpeta\excel_outputs"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Convertir la primera página a imagen
print("📄 Convirtiendo PDF a imagen...")
pages = convert_from_path(PDF_PATH, dpi=300, poppler_path=POPLER_BIN_PATH)
img_path = os.path.join(OUTPUT_DIR, 'pagina1_tabla.jpg')
pages[0].save(img_path, 'JPEG')

# Leer imagen en escala de grises y binarizar
img = cv2.imread(img_path)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)[1]

# Extraer texto con coordenadas
print("🔍 Aplicando OCR estructurado...")
data = pytesseract.image_to_data(thresh, output_type=Output.DICT)

words = []
for i in range(len(data['text'])):
    word = data['text'][i].strip()
    if word:
        x, y = data['left'][i], data['top'][i]
        words.append((y, x, word))

# Agrupar palabras por fila (por coordenadas Y)
words.sort()
rows = []
line = []
last_y = None
for y, x, word in words:
    if last_y is None or abs(y - last_y) < 15:
        line.append((x, word))
        last_y = y
    else:
        line.sort()
        rows.append([w for _, w in line])
        line = [(x, word)]
        last_y = y
if line:
    line.sort()
    rows.append([w for _, w in line])

# Unir pares de números rotos (ej: 327 642 → 327642)
clean_rows = []
for row in rows:
    combined = []
    i = 0
    while i < len(row):
        if (i + 1 < len(row) and row[i].isdigit() and row[i + 1].isdigit()):
            combined.append(row[i] + row[i + 1])
            i += 2
        else:
            combined.append(row[i])
            i += 1
    clean_rows.append(combined)

# Corregir errores en nombres de meses
meses_correctos = {
    "Enero": "Enero", "Febrero": "Febrero", "Marzo": "Marzo", "Abril": "Abril",
    "Abnil": "Abril", "Mayo": "Mayo", "Junio": "Junio", "Juho": "Julio", "Julio": "Julio",
    "Agosto": "Agosto", "Septiembre": "Septiembre", "Octubre": "Octubre",
    "Noviembre": "Noviembre", "Diciembre": "Diciembre", "Total": "Total"
}

final_rows = []
for row in clean_rows:
    if not row:
        continue
    mes = row[0]
    if mes in meses_correctos:
        row[0] = meses_correctos[mes]
        final_rows.append(row)

# Ajustar filas que tienen más de 8 columnas
header = ['Mes', '2017', '2018', '2019', '2020', '2021', '2022', '2023']
final_limpio = []
for row in final_rows:
    if len(row) >= 8:
        final_limpio.append(row[:8])  # solo las 8 primeras columnas (recorta si sobran)

# Crear DataFrame
df = pd.DataFrame(final_limpio, columns=header)

# Guardar en Excel
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
excel_path = os.path.join(OUTPUT_DIR, f'turismo_mensual_limpio_{timestamp}.xlsx')
df.to_excel(excel_path, index=False)

print(f"✅ Archivo Excel guardado correctamente: {excel_path}")




