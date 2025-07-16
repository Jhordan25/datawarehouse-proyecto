import pandas as pd
import pyodbc
import uuid
import os
# ----------- PARTE 1: Normalización del Excel -----------

# 1. Rutas
archivo_entrada = r"C:\\Users\\Usuario\Documents\\imagenes\\JOBS\\beneficios_resumidos(1).xlsx"
archivo_salida_excel = r"C:\\Users\\Usuario\Documents\\imagenes\\JOBS\\Normalizado\\Beneficios_normalizado_para_SQL.xlsx"

# Crear directorio de salida si no existe
os.makedirs(os.path.dirname(archivo_salida_excel), exist_ok=True)

# 2. Leer archivo
try:
    df = pd.read_excel(archivo_entrada, sheet_name="Hoja 1")
except FileNotFoundError:
    print(f"Error: No se encontró el archivo {archivo_entrada}")
    exit(1)

# 3. Verificar columnas iniciales
print("Columnas originales del Excel:")
print(df.columns.tolist())

# 4. Eliminar filas vacías
df = df.dropna(how='all')

# 5. Normalizar nombres de columnas (eliminar espacios iniciales/finales)
df.columns = df.columns.str.strip()

# 6. Renombrar columnas a nombres más adecuados para SQL
column_mapping = {
    'Titulo': 'Promocion',
    'Descripcion': 'Detalles',
    'Enlace': 'URL'
}

# Renombrar columnas
df.rename(columns=column_mapping, inplace=True)

# 7. Verificar que todas las columnas requeridas estén presentes
required_columns = ['Promocion', 'Detalles', 'URL']
missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    print(f"Advertencia: Faltan las columnas {missing_columns}. Se llenarán con valores predeterminados.")
    for col in missing_columns:
        df[col] = 'Sin_dato'

# 8. Agregar columna ID única
df['ID'] = [str(uuid.uuid4()) for _ in range(len(df))]

# 9. Mostrar columnas finales
print("Columnas después de renombrar:")
print(df.columns.tolist())

# 10. Reemplazar celdas vacías
for col in df.columns:
    df[col] = df[col].fillna('Sin_dato').astype(str)  # Convertir todo a string para consistencia

# 11. Verificar longitud de datos en Detalles
print("Verificando longitud de datos en 'Detalles':")
max_length = 0
for idx, value in df['Detalles'].items():
    length = len(str(value))
    max_length = max(max_length, length)
    if length > 4000:  # Advertencia para valores muy largos
        print(f"Advertencia: Fila {idx} en 'Detalles' tiene {length} caracteres.")
print(f"Longitud máxima en 'Detalles': {max_length} caracteres")

# 12. Verificar datos limpios
print("Primeras filas del DataFrame limpio:")
print(df.head())

# 13. Guardar Excel limpio
try:
    df.to_excel(archivo_salida_excel, index=False)
    print("Excel limpio generado correctamente.")
except Exception as e:
    print(f"Error al guardar el Excel: {e}")

# ----------- PARTE 2: Subida a SQL Server -----------

# 14. Conexión a SQL Server con autenticación de Windows
conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-UKFVAR1;"  # Cambiar según el servidor
    "DATABASE=DBCostaDelSol;"
    "Trusted_Connection=yes;"
)

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
except Exception as e:
    print(f"Error conectando a SQL Server: {e}")
    exit(1)

# 15. Eliminar tabla existente para asegurar el nuevo esquema
nombre_tabla = "dbo.BeneficiosPromocion"
cursor.execute(f"IF OBJECT_ID('{nombre_tabla}', 'U') IS NOT NULL DROP TABLE {nombre_tabla};")
conn.commit()

# 16. Crear tabla
def generar_sql_creacion(df, tabla):
    columnas_sql = []
    for col in df.columns:
        if col == 'ID':
            tipo_sql = "VARCHAR(36)"  # Para UUID
        elif col == 'Promocion':
            tipo_sql = "VARCHAR(100)"
        elif col == 'URL':
            tipo_sql = "VARCHAR(255)"
        elif col == 'Detalles':
            tipo_sql = "NVARCHAR(MAX)"  # Soporta textos largos
        else:
            tipo_sql = "NVARCHAR(1000)"
        columnas_sql.append(f"[{col}] {tipo_sql}")
    columnas_str = ", ".join(columnas_sql)
    return f"CREATE TABLE {tabla} ({columnas_str});"

cursor.execute(generar_sql_creacion(df, nombre_tabla))
conn.commit()

# 17. Insertar datos
columnas = ", ".join(f"[{col}]" for col in df.columns)
placeholders = ", ".join("?" for _ in df.columns)
sql_insert = f"INSERT INTO {nombre_tabla} ({columnas}) VALUES ({placeholders})"

for idx, fila in enumerate(df.itertuples(index=False)):
    try:
        cursor.execute(sql_insert, fila)
    except pyodbc.Error as e:
        print(f"Error insertando fila {idx} (Promocion: {fila[0]}): {e}")
        continue

conn.commit()
cursor.close()
conn.close()

print("Datos subidos a SQL Server correctamente.")