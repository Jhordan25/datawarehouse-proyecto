import pandas as pd
import pyodbc
import unidecode

# ----------- PARTE 1: Normalización del Excel -----------

archivo_entrada = r"c:\Users\Usuario\Documents\imagenes\JOBS\Tasas de interés nominal y real en MN y ME (cierre del año, en términos efectivos anuales) - (20 series).xlsx"
archivo_salida_excel = r"C:\Users\Usuario\Documents\imagenes\JOBS\Normalizado\Tasas_normalizado_para_SQL_long.xlsx"

# Leer archivo omitiendo primera fila
df = pd.read_excel(archivo_entrada, sheet_name=0, skiprows=1)
df = df.loc[:, df.columns.notna()]
df.replace("n.d.", pd.NA, inplace=True)

# Normalizar nombres de columnas
def limpiar_columna(col):
    col = str(col)
    col = unidecode.unidecode(col)
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

# Cambiar nombre de la primera columna si es necesario
if df.columns[0].lower().startswith("unnamed"):
    df.rename(columns={df.columns[0]: "anios"}, inplace=True)

# Convertir columnas a numéricas (excepto 'anios')
df[df.columns[0]] = df[df.columns[0]].fillna("Sin_dato")
for col in df.columns[1:]:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# ---- Convertir de ancho a largo ----
df_largo = df.melt(id_vars=["anios"], var_name="indicador", value_name="valor")

# Extraer partes del nombre del indicador para mejor análisis
# Ejemplo de columna original: Tasas_de_interes_nominal_y_real_en_MN_y_ME_cierre_del_ano_en_terminos_efectivos_anuales___MN___Prest_1
df_largo[["origen", "moneda", "tipo"]] = df_largo["indicador"].str.extract(r'(.+?)___(MN|ME)___([A-Za-z]+)')
df_largo.drop(columns=["indicador"], inplace=True)

# Reordenar
df_largo = df_largo[["anios", "moneda", "tipo", "valor"]]
df_largo["anios"] = pd.to_numeric(df_largo["anios"], errors="coerce").fillna(0).astype(int)

# Guardar Excel limpio en formato largo
df_largo.to_excel(archivo_salida_excel, index=False)
print("Excel limpio y en formato largo generado correctamente.")

# ----------- PARTE 2: Subida a SQL Server -----------

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-UKFVAR1;"
    "DATABASE=DBCostaDelSol;"
    "Trusted_Connection=yes;"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

nombre_tabla = "dbo.TasasInteresAnualLargo"

def generar_sql_creacion(df, tabla):
    tipo_map = {
        "int64": "INT",
        "float64": "FLOAT",
        "object": "VARCHAR(255)"
    }
    columnas_sql = []
    for col, tipo in df.dtypes.items():
        tipo_sql = tipo_map.get(str(tipo), "VARCHAR(255)")
        columnas_sql.append(f"[{col}] {tipo_sql}")
    columnas_str = ", ".join(columnas_sql)
    return f"IF OBJECT_ID('{tabla}', 'U') IS NULL CREATE TABLE {tabla} ({columnas_str});"

cursor.execute(generar_sql_creacion(df_largo, nombre_tabla))
conn.commit()

# Insertar los datos
columnas = ", ".join(f"[{col}]" for col in df_largo.columns)
placeholders = ", ".join("?" for _ in df_largo.columns)
sql_insert = f"INSERT INTO {nombre_tabla} ({columnas}) VALUES ({placeholders})"

for fila in df_largo.itertuples(index=False):
    cursor.execute(sql_insert, fila)

conn.commit()
cursor.close()
conn.close()

print("Datos subidos correctamente a SQL Server en formato largo.")
