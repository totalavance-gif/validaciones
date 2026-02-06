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
        # 1. [span_1](start_span)Datos del Contribuyente[span_1](end_span)
        nombre = request.form.get("nombre", "MARIANA MARTINEZ SOTELO").upper()
        rfc = request.form.get("rfc", "MASM980308217").upper()
        curp = request.form.get("curp", "MASM980308MMCRTR09").upper()
        idcif = request.form.get("idcif", "16040028836")
        fecha_inicio = request.form.get("fecha_inicio", "01 DE ABRIL DE 2016")

        # 2. [span_2](start_span)Datos del Domicilio[span_2](end_span)
        cp = request.form.get("cp", "56704")
        vialidad = request.form.get("vialidad", "CALLE").upper()
        nombre_vialidad = request.form.get("nombre_vialidad", "LIMON").upper()
        n_ext = request.form.get("n_ext", "SN")
        colonia = request.form.get("colonia", "CENTRO").upper()
        municipio = request.form.get("municipio", "TLALMANALCO").upper()
        entidad = request.form.get("entidad", "MEXICO").upper()

        # 3. Cargar PDF base
        current_dir = os.path.dirname(os.path.abspath(__file__))
        pdf_path = os.path.join(current_dir, "CUPY620808MPLRRL07_LIMPIO.pdf")
        doc = fitz.open(pdf_path)
        page = doc[0]
        
        f_reg, f_bold = "helv", "hebo"

        # --- BLOQUE CÉDULA (Superior Izquierda) ---
        page.insert_text(fitz.Point(165 - (len(rfc)*2), get_y(638)), rfc, fontsize=8, fontname=f_bold)
        page.insert_text(fitz.Point(165 - (len(nombre)*1.5), get_y(612)), nombre, fontsize=6.5, fontname=f_reg)
        page.insert_text(fitz.Point(165 - (len(f"idCIF: {idcif}")*1.5), get_y(595)), f"idCIF: {idcif}", fontsize=6.5, fontname=f_reg)

        # -[span_3](start_span)-- DATOS DE IDENTIFICACIÓN[span_3](end_span) ---
        page.insert_text(fitz.Point(255, get_y(452)), rfc, fontsize=7, fontname=f_reg)
        page.insert_text(fitz.Point(255, get_y(428.5)), curp, fontsize=7, fontname=f_reg)
        page.insert_text(fitz.Point(255, get_y(405)), nombre, fontsize=7, fontname=f_reg)
        page.insert_text(fitz.Point(255, get_y(381.5)), fecha_inicio, fontsize=7, fontname=f_reg)
        page.insert_text(fitz.Point(255, get_y(358)), "ACTIVO", fontsize=7, fontname=f_reg)

        # -[span_4](start_span)-- DATOS DEL DOMICILIO[span_4](end_span) ---
        page.insert_text(fitz.Point(255, get_y(293)), cp, fontsize=7, fontname=f_reg)
        page.insert_text(fitz.Point(440, get_y(293)), vialidad, fontsize=7, fontname=f_reg)
        page.insert_text(fitz.Point(255, get_y(270)), nombre_vialidad, fontsize=7, fontname=f_reg)
        page.insert_text(fitz.Point(440, get_y(270)), n_ext, fontsize=7, fontname=f_reg)
        page.insert_text(fitz.Point(255, get_y(246.5)), colonia, fontsize=7, fontname=f_reg)
        page.insert_text(fitz.Point(255, get_y(223)), municipio, fontsize=7, fontname=f_reg)
        page.insert_text(fitz.Point(255, get_y(199.5)), entidad, fontsize=7, fontname=f_reg)

        # 4. Finalización y Descarga
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
        
