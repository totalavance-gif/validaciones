import fitz  # PyMuPDF
import io
import os
from flask import Flask, request, send_file, render_template

app = Flask(__name__, template_folder='../templates')

def get_y(y_pt):
    # Convierte puntos de abajo-arriba a arriba-abajo (Base 792 pts)
    return 792 - y_pt

@app.route("/procesar", methods=["POST"])
def procesar():
    doc = None
    try:
        # 1. Datos del formulario
        nombre = request.form.get("nombre", "").upper()
        curp = request.form.get("curp", "").upper()
        rfc = request.form.get("rfc", curp[:13]).upper()
        idcif = request.form.get("idcif", "21030308867")

        # 2. Ruta al PDF base en la carpeta /api
        current_dir = os.path.dirname(os.path.abspath(__file__))
        pdf_path = os.path.join(current_dir, "CUPY620808MPLRRL07_LIMPIO.pdf")

        if not os.path.exists(pdf_path):
            return f"Error: No se encontró el PDF base en {pdf_path}", 404

        # 3. Editar PDF
        doc = fitz.open(pdf_path)
        page = doc[0]

        # SOLUCIÓN AL ERROR DE FUENTE: 
        # Usamos nombres clave que PyMuPDF reconoce internamente sin buscar archivos .ttf
        f_reg = "helv" 
        f_bold = "hebo" # "hebo" es el código interno para Helvetica-Bold

        # --- MAPEO CÉDULA ---
        # RFC (Bold)
        page.insert_text(fitz.Point(165 - (len(rfc)*2), get_y(638)), rfc, fontsize=8, fontname=f_bold)
        # Nombre
        page.insert_text(fitz.Point(165 - (len(nombre)*1.5), get_y(612)), nombre, fontsize=6.5, fontname=f_reg)
        # idCIF
        page.insert_text(fitz.Point(165 - (len(f"idCIF: {idcif}")*1.5), get_y(595)), f"idCIF: {idcif}", fontsize=6.5, fontname=f_reg)

        # --- MAPEO IDENTIFICACIÓN ---
        page.insert_text(fitz.Point(255, get_y(452)), rfc, fontsize=7, fontname=f_reg)
        page.insert_text(fitz.Point(255, get_y(428.5)), curp, fontsize=7, fontname=f_reg)
        page.insert_text(fitz.Point(255, get_y(405)), nombre, fontsize=7, fontname=f_reg)

        # 4. Generar salida en memoria
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
        # Captura el error "need font file or buffer" y otros
        return f"Ocurrió un error al generar el PDF: {str(e)}", 500
    finally:
        if doc:
            doc.close()

@app.route("/")
def home():
    return render_template("index.html")
    
