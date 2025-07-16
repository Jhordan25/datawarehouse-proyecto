import pandas as pd
import pyodbc
import unidecode
import os

# ----------- PARTE 1: Normalización del Excel -----------

# 1. Rutas
archivo_entrada = r"C:\Users\Usuario\Documents\imagenes\JOBS\sunat.xlsx"
archivo_salida_excel = r"C:\Users\Usuario\Documents\imagenes\JOBS\Normalizado\Sunat_normalizado_para_SQL.xlsx"

# Crear carpeta de salida si no existe
os.makedirs(os.path.dirname(archivo_salida_excel), exist_ok=True)

# 2. Leer archivo, omitir primera fila (encabezado genérico) y usar segunda fila como encabezado
df = pd.read_excel(archivo_entrada, sheet_name="PadronRUC_202501", skiprows=1)

# 3. Eliminar columnas sin nombre (NaN)
df = df.loc[:, df.columns.notna()]

# 4. Reemplazar "NO DISPONIBLE" por NA (nulo)
df.replace("NO DISPONIBLE", pd.NA, inplace=True)

# 5. Normalizar nombres de columnas y evitar duplicados
def limpiar_columna(col):
    col = str(col)
    col = unidecode.unidecode(col)  # Elimina tildes y eñes
    col = col.strip().replace(" ", "_")
    col = col.replace("(", "").replace(")", "").replace(",", "").replace("-", "_").replace(".", "")
    col = col.replace("%", "porc")
    col = ''.join(c for c in col if c.isalnum() or c == "_")
    return col[:100]

def limpiar_columnas_unicas(columnas):
    vistas = {}
    nuevas = []
    for col in columnas:
        base = limpiar_columna(col)
        nuevo = base
        contador = 1
        while nuevo in vistas:
            nuevo = f"{base}_{contador}"
            contador += 1
        vistas[nuevo] = True
        nuevas.append(nuevo)
    return nuevas

df.columns = limpiar_columnas_unicas(df.columns)

# 6. Mostrar columnas normalizadas
print("Columnas normalizadas:")
print(df.columns.tolist())

# 7. Convertir columnas numéricas específicas
numeric_columns = ["UBIGEO", "PERIODO_PUBLICACION"]
for col in numeric_columns:
    try:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    except Exception as e:
        print(f"Error convirtiendo la columna {col}: {e}")

# 8. Asegurar que RUC sea string
df["RUC"] = df["RUC"].astype(str)

# 9. Reemplazar nulos
for col in df.columns:
    if col in numeric_columns:
        df[col] = df[col].infer_objects(copy=False).fillna(0)  # Corrección para FutureWarning
    else:
        df[col] = df[col].infer_objects(copy=False).fillna("Sin_dato")

# 10. Guardar Excel limpio
df.to_excel(archivo_salida_excel, index=False)
print("Excel limpio generado correctamente.")

# ----------- PARTE 2: Subida a SQL Server -----------

# 11. Conexión a SQL Server con autenticación de Windows
conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-UKFVAR1;"
    "DATABASE=DBCostaDelSol;"
    "Trusted_Connection=yes;"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# 12. Crear tabla si no existe
nombre_tabla = "dbo.SunatEmpresas"

def generar_sql_creacion(df, tabla):
    tipo_map = {
        "int64": "INT",
        "float64": "FLOAT",
        "object": "VARCHAR(255)"
    }
    columnas_sql = []
    for col, tipo in df.dtypes.items():
        tipo_sql = tipo_map.get(str(tipo), "VARCHAR(255)")
        if col == "RUC":
            tipo_sql = "VARCHAR(11)"  # RUC tiene 11 dígitos
        columnas_sql.append(f"[{col}] {tipo_sql}")
    columnas_str = ", ".join(columnas_sql)
    return f"IF OBJECT_ID('{tabla}', 'U') IS NULL CREATE TABLE {tabla} ({columnas_str});"

cursor.execute(generar_sql_creacion(df, nombre_tabla))
conn.commit()

# 13. Insertar datos
columnas = ", ".join(f"[{col}]" for col in df.columns)
placeholders = ", ".join("?" for _ in df.columns)
sql_insert = f"INSERT INTO {nombre_tabla} ({columnas}) VALUES ({placeholders})"

for fila in df.itertuples(index=False):
    cursor.execute(sql_insert, fila)

conn.commit()
cursor.close()
conn.close()

print("Datos subidos a SQL Server correctamente.")