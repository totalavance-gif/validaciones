import fitz  # PyMuPDF
import io
import os
from flask import Flask, request, send_file, render_template

# Configuración de Flask apuntando a la carpeta de plantillas un nivel arriba
app = Flask(__name__, template_folder='../templates')

def get_y(y_pt):
    """Convierte coordenadas de ReportLab (puntos desde abajo) a PyMuPDF (puntos desde arriba)"""
    return 792 - y_pt

@app.route("/procesar", methods=["POST"])
def procesar():
    doc = None
    try:
        # 1. Recolección de datos desde el formulario
        nombre = request.form.get("nombre", "").upper()
        curp = request.form.get("curp", "").upper()
        # El RFC son los primeros 13 dígitos de la CURP o lo que el usuario envíe
        rfc = request.form.get("rfc", curp[:13]).upper()
        idcif = request.form.get("idcif", "21030308867")

        # 2. Localización del PDF base (Ubicado en /api/ junto a este index.py)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        pdf_path = os.path.join(current_dir, "CUPY620808MPLRRL07_LIMPIO.pdf")

        # Verificación de existencia del archivo para evitar Error 500
        if not os.path.exists(pdf_path):
            return f"Error: No se encontró el PDF base en {pdf_path}", 404

        # 3. Edición del PDF con PyMuPDF
        doc = fitz.open(pdf_path)
        page = doc[0]  # Primera página

        # Estilos de fuente estándar (Helvetica)
        f_bold = "helv-bold"
        f_reg = "helv"

        # --- MAPEO BLOQUE CÉDULA (Izquierda superior) ---
        # RFC (Bold y centrado manual aproximado)
        page.insert_text(fitz.Point(165 - (len(rfc)*2), get_y(638)), rfc, fontsize=8, fontname=f_bold)
        # Nombre
        page.insert_text(fitz.Point(165 - (len(nombre)*1.5), get_y(612)), nombre, fontsize=6.5, fontname=f_reg)
        # idCIF
        page.insert_text(fitz.Point(165 - (len(f"idCIF: {idcif}")*1.5), get_y(595)), f"idCIF: {idcif}", fontsize=6.5, fontname=f_reg)

        # --- MAPEO BLOQUE IDENTIFICACIÓN (Centro) ---
        # RFC
        page.insert_text(fitz.Point(255, get_y(452)), rfc, fontsize=7, fontname=f_reg)
        # CURP
        page.insert_text(fitz.Point(255, get_y(428.5)), curp, fontsize=7, fontname=f_reg)
        # Nombre Completo
        page.insert_text(fitz.Point(255, get_y(405)), nombre, fontsize=7, fontname=f_reg)

        # 4. Preparación de la descarga
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        
        return send_file(
            buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"CSF_{rfc}.pdf"
        )

    except Exception as e:
        # Esto capturará cualquier error y lo mostrará en el navegador para debug
        return f"Ocurrió un error al generar el PDF: {str(e)}", 500
    finally:
        if doc:
            doc.close()

@app.route("/")
def home():
    # Renderiza el formulario que ya confirmamos que funciona
    return render_template("index.html")

# Necesario para ejecución local si deseas probar
if __name__ == "__main__":
    app.run(debug=True)
    
