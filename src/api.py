# src/api.py
import os
from pathlib import Path
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

# CORRECCIÓN: Se añade un punto para el import relativo
from .parser_core import (EXTRACTORES, extraer_texto, limpiar_y_estructurar_texto)

# Inicializamos la aplicación Flask
app = Flask(__name__)

# Creamos una carpeta temporal para guardar los archivos que se suban
UPLOAD_FOLDER = Path("./temp_uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Definimos qué extensiones de archivo están permitidas
ALLOWED_EXTENSIONS = set(EXTRACTORES.keys())

def archivo_permitido(filename):
    """Comprueba si la extensión del archivo está permitida."""
    return '.' in filename and f".{filename.rsplit('.', 1)[1].lower()}" in ALLOWED_EXTENSIONS

@app.route('/procesar', methods=['POST'])
def procesar_archivo():
    """
    Punto de entrada (endpoint) de la API.
    Recibe un archivo, lo procesa y devuelve el texto limpio.
    """
    # 1. Comprobar si se ha enviado un archivo
    if 'file' not in request.files:
        return jsonify({"error": "No se ha enviado ningún archivo"}), 400
    
    file = request.files['file']

    # 2. Comprobar si el nombre del archivo es válido y tiene una extensión permitida
    if file.filename == '' or not archivo_permitido(file.filename):
        return jsonify({"error": "Tipo de archivo no permitido o archivo sin nombre"}), 400

    # 3. Guardar el archivo de forma segura en el servidor
    filename = secure_filename(file.filename)
    ruta_archivo = UPLOAD_FOLDER / filename
    file.save(ruta_archivo)

    try:
        # 4. Usar la lógica de parser_core.py para procesar el archivo
        texto_bruto = extraer_texto(str(ruta_archivo))
        if texto_bruto.startswith("Error:"):
            raise ValueError(texto_bruto)
        
        texto_limpio = limpiar_y_estructurar_texto(texto_bruto)

        # 5. Devolver el resultado en formato JSON
        return jsonify({
            "nombre_archivo": filename,
            "texto_procesado": texto_limpio
        })

    except Exception as e:
        # Si algo falla, devolver un error claro
        return jsonify({"error": f"Ha ocurrido un error al procesar el archivo: {e}"}), 500
    
    finally:
        # 6. Eliminar el archivo temporal después de procesarlo
        if ruta_archivo.exists():
            os.remove(ruta_archivo)

# Ruta principal para comprobar que la API está funcionando
@app.route('/')
def index():
    return "API de Dissentis.AI Parser está en funcionamiento."

if __name__ == '__main__':
    # Esto es solo para pruebas locales, no se usará en producción
    app.run(debug=True)
