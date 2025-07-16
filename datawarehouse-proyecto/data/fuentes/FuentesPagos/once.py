import pandas as pd
import pyodbc

# ----------- PARTE 1: Normalización del Excel -----------

# 1. Rutas
archivo_entrada = r"C:\Users\Usuario\Documents\imagenes\JOBS\comentarios_tiktok_resultado.xlsx"
archivo_salida_excel = r"C:\Users\Usuario\Documents\imagenes\JOBS\Normalizado\TikTok_comentarios_normalizado_para_SQL.xlsx"

# 2. Leer archivo
try:
    df = pd.read_excel(archivo_entrada, sheet_name="Sheet1")
except FileNotFoundError:
    print(f"Error: No se encontró el archivo {archivo_entrada}")
    exit(1)

# 3. Verificar columnas iniciales
print("Columnas originales del Excel:")
print(df.columns.tolist())

# 4. Eliminar fila 2 (index 0, row with 'Unique ID', 'Name', etc.)
df = df.drop(index=0)

# 5. Eliminar columnas vacías (todas NaN o vacías)
df = df.dropna(axis=1, how='all')

# 6. Eliminar columna Date (Columna5)
if 'Columna5' in df.columns:
    df = df.drop(columns='Columna5')

# 7. Renombrar columnas a las especificadas
column_mapping = {
    'Columna1': 'Numero',
    'Columna3': 'Unique ID',
    'Columna4': 'Name',
    'Columna6': 'Likes',
    'Comment': 'Comments',
    'Columna8': 'Profile ID',
    'Columna9': 'view source',
    'Sentimiento': 'Sentimiento',
    'Etiqueta': 'Etiqueta'
}

# Filtrar solo las columnas presentes y renombrar
available_columns = [col for col in column_mapping.keys() if col in df.columns]
df = df[available_columns]
df.rename(columns=column_mapping, inplace=True)

# 8. Verificar que todas las columnas requeridas estén presentes
required_columns = ['Numero', 'Unique ID', 'Name', 'Likes', 'Comments', 'Profile ID', 'view source', 'Sentimiento', 'Etiqueta']
missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    print(f"Advertencia: Faltan las columnas {missing_columns}. Se llenarán con valores predeterminados.")
    for col in missing_columns:
        if col in ['Numero', 'Likes', 'Sentimiento']:
            df[col] = 0
        else:
            df[col] = 'Sin_dato'

# 9. Mostrar columnas finales
print("Columnas después de renombrar:")
print(df.columns.tolist())

# 10. Identificar columnas numéricas
numeric_columns = ['Numero', 'Likes', 'Sentimiento']

# 11. Convertir columnas numéricas
for col in numeric_columns:
    if col in df.columns:
        try:
            if col == 'Sentimiento':
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0).astype(float)
            else:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        except Exception as e:
            print(f"Error convirtiendo la columna {col}: {e}")

# 12. Reemplazar celdas vacías
for col in df.columns:
    if col in numeric_columns:
        if col == 'Sentimiento':
            df[col] = df[col].fillna(0.0).infer_objects()
        else:
            df[col] = df[col].fillna(0).infer_objects()
    else:
        df[col] = df[col].fillna('Sin_dato').infer_objects()

# 13. Verificar datos limpios
print("Primeras filas del DataFrame limpio:")
print(df.head())

# 14. Guardar Excel limpio
df.to_excel(archivo_salida_excel, index=False)
print("Excel limpio generado correctamente.")

# ----------- PARTE 2: Subida a SQL Server -----------

# 15. Conexión a SQL Server con autenticación de Windows
conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-UKFVAR1;"
    "DATABASE=EJEMPLO;"
    "Trusted_Connection=yes;"
)

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
except Exception as e:
    print(f"Error conectando a SQL Server: {e}")
    exit(1)

# 16. Eliminar tabla existente para asegurar el nuevo esquema
nombre_tabla = "dbo.TikTokComentarioSentimientos"
cursor.execute(f"IF OBJECT_ID('{nombre_tabla}', 'U') IS NOT NULL DROP TABLE {nombre_tabla};")
conn.commit()

# 17. Crear tabla
def generar_sql_creacion(df, tabla):
    tipo_map = {
        "int64": "INT",
        "float64": "FLOAT",
        "object": "VARCHAR(255)"
    }
    columnas_sql = []
    for col, tipo in df.dtypes.items():
        tipo_sql = tipo_map.get(str(tipo), "VARCHAR(255)")
        if col == 'Comments':
            tipo_sql = "NVARCHAR(1000)"
        elif col == 'Unique ID':
            tipo_sql = "VARCHAR(50)"
        elif col == 'Name':
            tipo_sql = "VARCHAR(100)"
        elif col == 'Profile ID':
            tipo_sql = "VARCHAR(20)"
        elif col in ['view source', 'Etiqueta']:
            tipo_sql = "VARCHAR(50)"
        columnas_sql.append(f"[{col}] {tipo_sql}")
    columnas_str = ", ".join(columnas_sql)
    return f"CREATE TABLE {tabla} ({columnas_str});"

cursor.execute(generar_sql_creacion(df, nombre_tabla))
conn.commit()

# 18. Insertar datos
columnas = ", ".join(f"[{col}]" for col in df.columns)
placeholders = ", ".join("?" for _ in df.columns)
sql_insert = f"INSERT INTO {nombre_tabla} ({columnas}) VALUES ({placeholders})"

for fila in df.itertuples(index=False):
    cursor.execute(sql_insert, fila)

conn.commit()
cursor.close()
conn.close()

print("Datos subidos a SQL Server correctamente.")