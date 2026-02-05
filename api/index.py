import fitz  # PyMuPDF
import io
import os
from flask import Flask, request, send_file, render_template

app = Flask(__name__, template_folder='../templates')

# Función para convertir coordenadas (ReportLab 0,0 abajo -> PyMuPDF 0,0 arriba)
def get_y(y_pt):
    return 792 - y_pt

@app.route("/procesar", methods=["POST"])
def procesar():
    doc = None
    try:
        # 1. Recuperar datos del formulario
        nombre = request.form.get("nombre", "").upper()
        curp = request.form.get("curp", "").upper()
        rfc = request.form.get("rfc", curp[:13]).upper()
        idcif = request.form.get("idcif", "21030308867")

        # 2. Ruta al PDF base (ubicado en la misma carpeta /api)
        base_path = os.path.dirname(os.path.abspath(__file__))
        pdf_path = os.path.join(base_path, "CUPY620808MPLRRL07_LIMPIO.pdf")

        if not os.path.exists(pdf_path):
            return f"Error: No se encontró el PDF base en {pdf_path}", 404

        # 3. Abrir y editar el PDF
        doc = fitz.open(pdf_path)
        page = doc[0]

        # Estilos de fuente
        f_bold = "helv-bold"
        f_reg = "helv"

        # --- MAPEO PÁGINA 1 ---
        # RFC en Cédula (Centrado manual aproximado)
        page.insert_text(fitz.Point(165 - (len(rfc)*2), get_y(638)), rfc, fontsize=8, fontname=f_bold)
        # Nombre en Cédula
        page.insert_text(fitz.Point(165 - (len(nombre)*1.5), get_y(612)), nombre, fontsize=6.5, fontname=f_reg)
        # idCIF
        page.insert_text(fitz.Point(165 - (len(f"idCIF: {idcif}")*1.5), get_y(595)), f"idCIF: {idcif}", fontsize=6.5, fontname=f_reg)

        # Bloque Identificación (RFC, CURP, Nombre)
        page.insert_text(fitz.Point(255, get_y(452)), rfc, fontsize=7, fontname=f_reg)
        page.insert_text(fitz.Point(255, get_y(428.5)), curp, fontsize=7, fontname=f_reg)
        page.insert_text(fitz.Point(255, get_y(405)), nombre, fontsize=7, fontname=f_reg)

        # 4. Generar el archivo de salida
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
        return f"Error crítico: {str(e)}", 500
    finally:
        if doc:
            doc.close()

@app.route("/")
def home():
    return render_template("index.html")
      
