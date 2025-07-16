import pandas as pd
import pyodbc
import re
from collections import Counter
from datetime import datetime
import nltk
from nltk.corpus import stopwords

# Descargar stopwords solo una vez
nltk.download('stopwords')

# Conexión a SQL Server
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-8GUFU2S\\SQL2022;"
    "DATABASE=DBCostaDelSol;"
    "Trusted_Connection=yes;"
)
cursor = conn.cursor()

# Leer archivo Excel
df = pd.read_excel("E:/Big Data/beneficios_resumidos.xlsx")

# Normalizar encabezados
df.columns = df.columns.str.strip().str.lower()

# Listas base
stop_words = set(stopwords.words('spanish'))
destinos = ['Tumbes', 'Piura', 'Chiclayo', 'Trujillo Golf', 'Trujillo Centro', 'Cajamarca',
            'Lima Aeropuerto', 'Lima Salaverry', 'Arequipa', 'Cusco', 'Pucallpa', 'Lima City']

entidades_tipo = {
    'BCP': 'Banco',
    'BBVA': 'Banco',
    'IO': 'Operador',
    'OH': 'Tarjeta',
    'AUNA': 'Salud',
    'BITEL': 'Operador',
    'CLUB DE LECTORES': 'Club',
    'BANBIF': 'Banco',
    'CMR': 'Tarjeta',
    'SCOTIABANK': 'Banco',
    'CLUB MILES': 'Club'
}

frecuencia_global = Counter()

# Limpiar tabla de palabras antes de insertar nuevas
cursor.execute("DELETE FROM PalabrasFrecuentesGlobales")
conn.commit()

# Procesar cada fila
for _, row in df.iterrows():
    titulo = str(row['titulo'])
    descripcion = str(row['descripcion'])

    # Insertar beneficio original
    cursor.execute("""
        INSERT INTO BeneficiosOriginales (Titulo, Descripcion)
        OUTPUT INSERTED.Id
        VALUES (?, ?)
    """, (titulo, descripcion))
    beneficio_id = cursor.fetchone()[0]
    conn.commit()

    # Frecuencia de palabras
    palabras = re.findall(r'\b\w+\b', descripcion.lower())
    palabras_filtradas = [p for p in palabras if p not in stop_words and len(p) > 2]
    frecuencia_global.update(palabras_filtradas)

    # Fechas detectadas (básicas)
    fechas = re.findall(r'\d{1,2}\s*(al|-)?\s*\d{1,2}\s*de\s+\w+|\d{1,2}/\d{1,2}/\d{4}|\d{4}', descripcion)
    for fecha in fechas:
        cursor.execute("""
            INSERT INTO FechasDetectadas (IdBeneficio, FechaDetectada, Tipo)
            VALUES (?, ?, ?)
        """, (beneficio_id, None, fecha.strip()))

    # Destinos mencionados
    for destino in destinos:
        if destino.lower() in descripcion.lower():
            cursor.execute("""
                INSERT INTO DestinosMencionados (IdBeneficio, Destino)
                VALUES (?, ?)
            """, (beneficio_id, destino))

    # Entidades
    for entidad, tipo in entidades_tipo.items():
        if entidad in titulo.upper():
            cursor.execute("""
                INSERT INTO EntidadesRelacionadas (IdBeneficio, Entidad, TipoEntidad)
                VALUES (?, ?, ?)
            """, (beneficio_id, entidad, tipo))

    conn.commit()

# Insertar frecuencias globales
for palabra, frecuencia in frecuencia_global.most_common():
    cursor.execute("""
        INSERT INTO PalabrasFrecuentesGlobales (Token, FrecuenciaTotal)
        VALUES (?, ?)
    """, (palabra, frecuencia))

conn.commit()
conn.close()
print("✅ Analítica de texto completada y cargada a SQL Server.")
