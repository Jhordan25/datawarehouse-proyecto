import pandas as pd
import re

# Palabras clave
positivas = ["excelente", "bueno", "genial", "recomendado", "agradable", "perfecto", "fantastico", "buen dato", "resolviendo", "gracias", "amor", "mejor información", "super", "super útil", "datazooo", "datazo", "información necesaria", "me encanta",
"feliz de ayudarlos", "yeiii", "aww", "👏", "🙌", "❤", "👍🏻", "😍", "👏👏👏", "👏👏👏👏", "🔥", "🌞", "informada", "util", "que buena info", "gracias por la info", "te gustaría más info", "qué otro dato te gustaría saber"]
negativas = ["malo", "horrible", "terrible", "pesimo", "deficiente", "desagradable", "lento", "desastre", "cagado", "espacio desperdicio", "debería de seguir funcionando", "nuevo es un desastre", "va ser dejado atrás", "políticos de mi3rd@", "en buen estado va ser dejado atrás"]

# Función para quitar emojis
def eliminar_emojis(texto):
    if not isinstance(texto, str):
        return texto
    # Esta regex elimina la mayoría de emojis
    return re.sub(r"[^\w\s,.!?¿¡@%$&#():;/-]", "", texto)

# Clasificar comentarios
def clasificar(comentario):
    if not isinstance(comentario, str):
        return ""
    comentario_sin_emojis = eliminar_emojis(comentario)
    c = comentario_sin_emojis.lower()
    if any(p in c for p in positivas):
        return "P"
    elif any(n in c for n in negativas):
        return "N"
    else:
        return ""

# Cargar Excel
df = pd.read_excel(r"C:\CargaExcel\FuentesBigData\Instagram\comentarios_instagram.xlsx")

# Limpiar emojis y clasificar
df["Comentario"] = df["Comentario"].apply(eliminar_emojis)
df["Tipo"] = df["Comentario"].apply(clasificar)

# Guardar nuevo Excel
df.to_excel("comentarios_clasificados.xlsx", index=False)
print("✅ Clasificación guardada en comentarios_clasificados.xlsx sin emojis")