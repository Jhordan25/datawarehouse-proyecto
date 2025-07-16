import pandas as pd
import os

# -------------------------------
# Configuración de rutas
# -------------------------------
input_excel_path = r'C:\Users\Usuario\Desktop\instagram\comentarios_instagrammm.xlsx'
output_excel_path = r'C:\Users\Usuario\Desktop\instagram\comentarios_clasificados.xlsx'

# -------------------------------
# Función de análisis de sentimientos simple
# -------------------------------
def simple_sentiment_analysis(comment):
    comment_lower = str(comment).lower()
    positive_keywords = [
        'felicidades', 'felicitaciones', 'gran logro', '🎉', '👏', '👍',
        'gracias', 'orgullo', 'bien', 'lo máximo', 'enhorabuena',
        'querido', 'maravilla', 'hermoso', 'lindo', 'bendiciones'
    ]
    negative_keywords = [
        'no funcionan', 'triste', 'llorar', 'malo', 'mal', 'reclamo',
        'mejoren', 'error', 'defecto', 'crítica', 'feo', 'horrible'
    ]

    if any(word in comment_lower for word in positive_keywords):
        return 'Positivo'
    elif any(word in comment_lower for word in negative_keywords):
        return 'Negativo'
    else:
        return 'Neutral'

# -------------------------------
# Lectura y procesamiento
# -------------------------------
try:
    df = pd.read_excel(input_excel_path)

    # Renombrar columnas a formato uniforme
    df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]

    # Verificar columnas necesarias
    required_columns = {'id', 'author', 'date', 'comment'}
    if not required_columns.issubset(set(df.columns)):
        raise Exception(f"❌ Faltan columnas requeridas: {required_columns - set(df.columns)}")

    # Aplicar análisis de sentimiento
    df['sentiment'] = df['comment'].apply(simple_sentiment_analysis)

    # Reordenar columnas
    df = df[['id', 'author', 'date', 'comment', 'sentiment']]

    # Guardar como archivo Excel (.xlsx)
    df.to_excel(output_excel_path, index=False)

    print(f"✅ Archivo Excel generado correctamente en: {output_excel_path}")
    print(df.head())

except FileNotFoundError:
    print(f"❌ Archivo no encontrado en: {input_excel_path}")
except Exception as e:
    print(f"❌ Error: {e}")

