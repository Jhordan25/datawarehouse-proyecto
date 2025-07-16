import requests
import os
import pandas as pd
from datetime import datetime
import re
import pyodbc  # Added for SQL Server interaction
import unidecode  # Added for column name normalization

# Configuración
API_KEY = 'sec_dfMnjl46pGEk8nBBZ9vnuuJDWGKnIh7M'
PDF_PATH = r'C:\Users\Usuario\Documents\imagenes\JOBS\Doc3.pdf'
PREDEFINED_MESSAGE = 'DAME LAS METRICAS A LO LARGO DE LOS AÑOS Y ACOMODALAS EN UNA TABLA'
CHATPDF_API_URL = 'https://api.chatpdf.com/v1'
OUTPUT_DIR = r'C:\Users\Usuario\Documents\imagenes\JOBS\Normalizado'

# Crear directorio de salida si no existe
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Headers para las solicitudes de API
headers = {
    'x-api-key': API_KEY,
    'Content-Type': 'application/json',
}

def upload_pdf(file_path):
    """Sube un PDF a ChatPDF y devuelve el source ID."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF no encontrado en {file_path}")
    
    files = [('file', ('file', open(file_path, 'rb'), 'application/octet-stream'))]
    upload_headers = {'x-api-key': API_KEY}
    
    response = requests.post(f'{CHATPDF_API_URL}/sources/add-file', headers=upload_headers, files=files)
    if response.status_code == 200:
        return response.json()['sourceId']
    else:
        raise Exception(f"Error al subir: {response.status_code} - {response.text}")

def chat_with_pdf(source_id, message):
    """Envía un mensaje al PDF y devuelve la respuesta."""
    data = {
        'sourceId': source_id,
        'messages': [{'role': 'user', 'content': message}],
        'referenceSources': True
    }
    
    response = requests.post(f'{CHATPDF_API_URL}/chats/message', headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error en chat: {response.status_code} - {response.text}")

def parse_table_from_response(content):
    """Parsea la respuesta de ChatPDF (formato tabla) y convierte a DataFrame."""
    try:
        print("Contenido de la respuesta de ChatPDF:")
        print(content)

        # Verificar si la respuesta contiene una tabla (buscando palabras clave como "Año")
        if "Año" not in content:
            raise ValueError("No se encontró una tabla en la respuesta.")

        # Dividir el contenido en líneas
        lines = content.split('\n')
        data = []
        headers = ['Año', 'Llegada de turistas internacionales (millones)']
        
        # Buscar filas de datos (puede ser Markdown, texto plano, etc.)
        for line in lines:
            # Ignorar líneas vacías o de formato (como separadores de tabla Markdown)
            if not line.strip() or line.startswith('-') or line.startswith('|----'):
                continue
            
            # Intentar parsear la línea como una fila de tabla
            # Ejemplo de formatos esperados: "| 2020 | 123.4 |" o "2020 123.4"
            match = re.match(r'\|?\s*(\d{4})\s*[|]?\s*([\d.,]+)\s*[|]?\s*', line)
            if match:
                year = match.group(1).strip()
                value = match.group(2).strip().replace(',', '.')  # Normalizar decimales
                
                # Validar y limpiar el valor numérico
                try:
                    value = float(value)
                except ValueError:
                    value = 'N/A'
                
                data.append([year, value])
        
        # Si no se encontraron datos, intentar un parseo más genérico
        if not data:
            for line in lines:
                # Buscar líneas con un año y un número
                match = re.match(r'(\d{4})\s+([\d.,]+)', line)
                if match:
                    year = match.group(1).strip()
                    value = match.group(2).strip().replace(',', '.')
                    try:
                        value = float(value)
                    except ValueError:
                        value = 'N/A'
                    data.append([year, value])
        
        # Crear DataFrame
        if data:
            df = pd.DataFrame(data, columns=headers)
            print("Datos extraídos:")
            print(df)
            return df
        else:
            print("No se encontraron datos válidos para la tabla.")
            return pd.DataFrame([['N/A', 'No data']], columns=headers)
            
    except Exception as e:
        print(f"Error al parsear tabla: {str(e)}")
        return pd.DataFrame([['N/A', f"Error: {str(e)}"]], columns=['Año', 'Llegada de turistas internacionales (millones)'])

def save_to_excel(df, filename_prefix):
    """Guarda el DataFrame en un archivo Excel, reemplazando si ya existe."""
    try:
        excel_path = os.path.join(OUTPUT_DIR, f'{filename_prefix}.xlsx')
        df.to_excel(excel_path, index=False, engine='openpyxl')
        print(f"Archivo Excel guardado/reemplazado: {excel_path}")
    except Exception as e:
        print(f"Error al guardar Excel: {str(e)}. Instala 'openpyxl' con 'pip install openpyxl' si falta.")

def upload_to_sql_server(df):
    """Sube el DataFrame a SQL Server."""
    try:
        # Normalizar nombres de columnas
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
        print("Columnas normalizadas para SQL:")
        print(df.columns.tolist())

        # Reemplazar 'N/A' y mensajes de error por NA
        df.replace(['N/A', 'No data', r'Error:.*'], pd.NA, regex=True, inplace=True)

        # Convertir columnas a tipos adecuados
        ano_col = next((c for c in df.columns if c.startswith("Ano")), None)
        turistas_col = next((c for c in df.columns if c.startswith("Llegada_de_turistas_internacionales_millones")), None)

        if ano_col:
            df[ano_col] = pd.to_numeric(df[ano_col], errors='coerce').fillna(0).astype(int)
        else:
            print("Error: No se encontró la columna 'Ano' después de normalización.")

        if turistas_col:
            df[turistas_col] = pd.to_numeric(df[turistas_col], errors='coerce').fillna(0.0).astype(float)
        else:
            print("Error: No se encontró la columna 'Llegada_de_turistas_internacionales_millones' después de normalización.")

        # Reemplazar nulos
        for col in df.columns:
            if col == ano_col:
                df[col] = df[col].fillna(0).infer_objects()
            elif col == turistas_col:
                df[col] = df[col].fillna(0.0).infer_objects()
            else:
                df[col] = df[col].fillna("Sin_dato").infer_objects()

        # Conexión a SQL Server
        conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=DESKTOP-UKFVAR1;"  # Cambia si corresponde
            "DATABASE=DBCostaDelSol;"        # Cambia si corresponde
            "Trusted_Connection=yes;"
        )

        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # Crear tabla si no existe
        nombre_tabla = "dbo.TuristasMetricas"

        def generar_sql_creacion(df, tabla):
            tipo_map = {
                "int64": "INT",
                "float64": "FLOAT",
                "object": "VARCHAR(255)"
            }
            columnas_sql = []
            for col, tipo in df.dtypes.items():
                tipo_sql = tipo_map.get(str(tipo), "VARCHAR(255)")
                if col.startswith("Ano"):
                    tipo_sql = "INT"
                if col.startswith("Llegada_de_turistas_internacionales_millones"):
                    tipo_sql = "FLOAT"
                columnas_sql.append(f"[{col}] {tipo_sql}")
            columnas_str = ", ".join(columnas_sql)
            return f"IF OBJECT_ID('{tabla}', 'U') IS NULL CREATE TABLE {tabla} ({columnas_str});"

        cursor.execute(generar_sql_creacion(df, nombre_tabla))
        conn.commit()

        # Insertar datos
        columnas = ", ".join(f"[{col}]" for col in df.columns)
        placeholders = ", ".join("?" for _ in df.columns)
        sql_insert = f"INSERT INTO {nombre_tabla} ({columnas}) VALUES ({placeholders})"

        for fila in df.itertuples(index=False):
            cursor.execute(sql_insert, fila)

        conn.commit()
        cursor.close()
        conn.close()

        print("Datos subidos a SQL Server correctamente.")

    except Exception as e:
        print(f"Error al subir a SQL Server: {str(e)}")

def main():
    try:
        print(f"Procesando PDF a las {datetime.now().strftime('%I:%M %p -05, %d de %B de %Y')}...")
        
        # Verificar que el archivo PDF existe
        print(f"Ruta del PDF: {PDF_PATH}")
        if not os.path.exists(PDF_PATH):
            raise FileNotFoundError(f"No se encontró el archivo PDF en la ruta: {PDF_PATH}")
        
        # Subir el PDF
        source_id = upload_pdf(PDF_PATH)
        print(f"Source ID: {source_id}")
        
        # Enviar mensaje y obtener respuesta
        chat_response = chat_with_pdf(source_id, PREDEFINED_MESSAGE)
        print("Respuesta de ChatPDF:")
        print(f"Contenido: {chat_response['content']}")
        
        # Parsear y guardar tabla en Excel
        table_df = parse_table_from_response(chat_response['content'])
        print("Primeras filas del DataFrame:")
        print(table_df.head())
        
        save_to_excel(table_df, "metricas_anuales")
        
        # Subir a SQL Server
        upload_to_sql_server(table_df)
        
        # Imprimir referencias si están disponibles
        if 'references' in chat_response:
            print("Referencias:")
            for ref in chat_response['references']:
                print(f"Página {ref['pageNumber']}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()