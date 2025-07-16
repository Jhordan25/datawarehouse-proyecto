import pandas as pd
from textblob import TextBlob

# Ruta al archivo Excel
archivo = r'C:\Users\Javie\Desktop\Analitica\comentarios_tiktok.xlsx'
df = pd.read_excel(archivo)

# Verifica si existe la columna 'Comment'
if 'Comment' not in df.columns:
    print("❌ La columna 'Comment' no existe. Columnas disponibles:")
    print(df.columns)
    raise Exception("Revisa el nombre exacto de la columna en el Excel")

# Análisis de sentimiento
def analizar_sentimiento(texto):
    if pd.isnull(texto):
        return 0
    blob = TextBlob(str(texto))
    return blob.sentiment.polarity

df['Sentimiento'] = df['Comment'].apply(analizar_sentimiento)

# Clasificación según polaridad
def clasificar(polaridad):
    if polaridad > 0:
        return 'Positivo'
    elif polaridad < 0:
        return 'Negativo'
    else:
        return 'Neutro'

df['Etiqueta'] = df['Sentimiento'].apply(clasificar)

# Guarda resultados en un nuevo Excel
df.to_excel('comentarios_tiktok_resultado.xlsx', index=False)

print("✅ Análisis completado. Archivo generado: comentarios_tiktok_resultado.xlsx")
