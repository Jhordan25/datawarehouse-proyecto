import pandas as pd
import pyodbc
import unidecode

# ----------- PARTE 1: Normalización y transformación del Excel -----------

archivo_entrada = r"C:\Users\Usuario\Documents\imagenes\JOBS\Reporte_Cifras(3).xlsx"
archivo_salida_excel = r"C:\Users\Usuario\Documents\imagenes\JOBS\Normalizado\Turistas_normalizado_para_SQL_largo.xlsx"

# Leer Excel, omitiendo filas iniciales
df = pd.read_excel(archivo_entrada, sheet_name="Lleg Tur Internac", skiprows=4)
df = df.loc[:, df.columns.notna()]  # Eliminar columnas vacías

# Renombrar primeras columnas
df.rename(columns={df.columns[0]: "Ranking", df.columns[1]: "Pais_Residencia"}, inplace=True)

# Eliminar filas vacías y "Resto del Mundo"
df = df.dropna(subset=["Pais_Residencia"])
df = df[df["Pais_Residencia"] != "Resto del Mundo"]

# Limpiar columnas y tipos
df["Ranking"] = df["Ranking"].fillna(0).astype(int)
df["Pais_Residencia"] = df["Pais_Residencia"].str.strip()

# Convertir columnas de años a enteros
for col in df.columns[2:]:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

# Transformar de wide → long
df_largo = df.melt(
    id_vars=["Ranking", "Pais_Residencia"],
    var_name="Anio",
    value_name="Cantidad"
)

# Asegurar tipos correctos
df_largo["Anio"] = df_largo["Anio"].astype(int)
df_largo["Cantidad"] = df_largo["Cantidad"].astype(int)

# Guardar versión larga
df_largo.to_excel(archivo_salida_excel, index=False)
print("Excel limpio y transformado generado correctamente.")

# ----------- PARTE 2: Subida a SQL Server -----------

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-UKFVAR1;"
    "DATABASE=DBCostaDelSol;"
    "Trusted_Connection=yes;"
)
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

nombre_tabla = "dbo.TuristasInternacionales_Largo"

# Crear tabla
sql_creacion = f"""
IF OBJECT_ID('{nombre_tabla}', 'U') IS NULL
CREATE TABLE {nombre_tabla} (
    Ranking INT,
    Pais_Residencia VARCHAR(255),
    Anio INT,
    Cantidad INT
);
"""
cursor.execute(sql_creacion)
conn.commit()

# Insertar datos
columnas = ", ".join(f"[{col}]" for col in df_largo.columns)
placeholders = ", ".join("?" for _ in df_largo.columns)
sql_insert = f"INSERT INTO {nombre_tabla} ({columnas}) VALUES ({placeholders})"

for fila in df_largo.itertuples(index=False):
    cursor.execute(sql_insert, fila)

conn.commit()
cursor.close()
conn.close()

print("Datos subidos a SQL Server correctamente en formato largo.")
