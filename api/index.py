import fitz
import io
import os
from flask import Flask, request, send_file, render_template

app = Flask(__name__, template_folder='../templates')

def get_y(y_pt):
    return 792 - y_pt

@app.route("/procesar", methods=["POST"])
def procesar():
    doc = None
    try:
        # 1. Captura de Datos (Asegúrate de agregarlos a tu index.html)
        nombre = request.form.get("nombre", "").upper()
        curp = request.form.get("curp", "").upper()
        rfc = request.form.get("rfc", curp[:13]).upper()
        idcif = request.form.get("idcif", "21030308867")
        
        # Datos de ejemplo para coherencia (puedes volverlos variables de formulario)
        cp = request.form.get("cp", "06300")
        colonia = request.form.get("colonia", "CENTRO").upper()
        municipio = request.form.get("municipio", "CUAUHTÉMOC").upper()
        estado = request.form.get("estado", "CIUDAD DE MÉXICO").upper()
        calle = request.form.get("calle", "AV. HIDALGO").upper()
        n_ext = request.form.get("n_ext", "77")

        current_dir = os.path.dirname(os.path.abspath(__file__))
        pdf_path = os.path.join(current_dir, "CUPY620808MPLRRL07_LIMPIO.pdf")

        doc = fitz.open(pdf_path)
        page = doc[0]
        f_reg = "helv"
        f_bold = "hebo"

        # --- SECCIÓN 1: CÉDULA (Arriba Izquierda) ---
        page.insert_text(fitz.Point(165 - (len(rfc)*2), get_y(638)), rfc, fontsize=8, fontname=f_bold)
        page.insert_text(fitz.Point(165 - (len(nombre)*1.5), get_y(612)), nombre, fontsize=6.5, fontname=f_reg)
        page.insert_text(fitz.Point(165 - (len(f"idCIF: {idcif}")*1.5), get_y(595)), f"idCIF: {idcif}", fontsize=6.5, fontname=f_reg)

        # --- SECCIÓN 2: DATOS DE IDENTIFICACIÓN ---
        page.insert_text(fitz.Point(255, get_y(452)), rfc, fontsize=7, fontname=f_reg)
        page.insert_text(fitz.Point(255, get_y(428.5)), curp, fontsize=7, fontname=f_reg)
        page.insert_text(fitz.Point(255, get_y(405)), nombre, fontsize=7, fontname=f_reg)
        # Fecha de inicio operaciones (Ejemplo)
        page.insert_text(fitz.Point(255, get_y(381.5)), "01/01/2010", fontsize=7, fontname=f_reg)
        # Estatus
        page.insert_text(fitz.Point(255, get_y(358)), "ACTIVO", fontsize=7, fontname=f_reg)

        # --- SECCIÓN 3: DATOS DEL DOMICILIO (Coherencia) ---
        page.insert_text(fitz.Point(255, get_y(293)), cp, fontsize=7, fontname=f_reg)
        page.insert_text(fitz.Point(255, get_y(270)), f"{calle} EXT: {n_ext}", fontsize=7, fontname=f_reg)
        page.insert_text(fitz.Point(255, get_y(246.5)), colonia, fontsize=7, fontname=f_reg)
        page.insert_text(fitz.Point(255, get_y(223)), municipio, fontsize=7, fontname=f_reg)
        page.insert_text(fitz.Point(255, get_y(199.5)), estado, fontsize=7, fontname=f_reg)

        # --- SECCIÓN 4: ACTIVIDADES Y REGÍMENES (Basado en tu imagen) ---
        # Actividad
        page.insert_text(fitz.Point(55, get_y(114)), "Servicios de contabilidad y auditoría", fontsize=6, fontname=f_reg)
        page.insert_text(fitz.Point(400, get_y(114)), "100%", fontsize=6, fontname=f_reg)
        
        # Régimen
        page.insert_text(fitz.Point(55, get_y(60)), "Régimen Simplificado de Confianza", fontsize=6, fontname=f_reg)
        page.insert_text(fitz.Point(400, get_y(60)), "01/01/2022", fontsize=6, fontname=f_reg)

        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        
        return send_file(buffer, mimetype="application/pdf", as_attachment=True, download_name=f"CSF_{rfc}.pdf")

    except Exception as e:
        return f"Error: {str(e)}", 500
    finally:
        if doc: doc.close()

@app.route("/")
def home():
    return render_template("index.html")
        
