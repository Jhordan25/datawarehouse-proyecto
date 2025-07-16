import os
import pyodbc
from docx import Document 
import fitz #PyMuPDF 


# --- Configuración SQL Server ---
server = r"LAPTOP-ONA0KC8I\SQL2022"
database = "hotelcostadelsol_peru"
conn_str = f"DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"

# --- Ruta de la carpeta que contiene los documentos ---
ruta_carpeta = r"C:\Users\LENOVO\Documents\Integracion_textos"

def insertar_datos(nombre_archivo, contenido):
    conn = None
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # --- Insertar los datos en la base de datos
        cursor.execute("""
            INSERT INTO dbo.TextData (NombreArchivo, Contenido)
            VALUES (?, ?)
            """, nombre_archivo, contenido)

        conn.commit()
        print(f"✅ Archivo insertado: {nombre_archivo}")
    except pyodbc.IntegrityError: # Falta 'as e' aquí, lo que causaría un NameError si 'e' se usa
        print(f"⚠️ Entrada duplicada: {e}") # 'e' no está definida en este bloque except
    except Exception as e:
        print(f"❌ Error al insertar: {str(e)[:100]}...")
    finally:
        if conn: # Solo intenta cerrar si conn existe
            conn.close()

def leer_txt(ruta_archivo):
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"❌ Error al leer archivo .txt: {e}")
        return None

def leer_word(ruta_archivo):
    try:
        doc = Document(ruta_archivo)
        contenido = "\n".join([p.text for p in doc.paragraphs])
        return contenido
    except Exception as e:
        print(f"❌ Error al leer archivo .docx: {e}")
        return None

def leer_pdf(ruta_archivo):
    try:
        # Abrir el archivo PDF
        doc = fitz.open(ruta_archivo)
        contenido = ""

        # Iterar sobre todas las páginas y extraer el texto
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            contenido += page.get_text("text") # Extraer todo el texto de la página

        return contenido
    except Exception as e:
        print(f"❌ Error al leer archivo .pdf: {e}")
        return None

def procesar_archivos():
    for archivo in os.listdir(ruta_carpeta):
        ruta_completa = os.path.join(ruta_carpeta, archivo)

        if archivo.lower().endswith('.txt'):
            # Leer archivos .txt
            contenido = leer_txt(ruta_completa)
            if contenido:
                insertar_datos(archivo, contenido)

        elif archivo.lower().endswith('.docx'):
            # Leer archivos .docx
            contenido = leer_word(ruta_completa)
            if contenido:
                insertar_datos(archivo, contenido)

        elif archivo.lower().endswith('.pdf'):
            # Leer archivos .pdf
            contenido = leer_pdf(ruta_completa)
            if contenido:
                insertar_datos(archivo, contenido)

# Ejecutar el procesamiento de los archivos
procesar_archivos()