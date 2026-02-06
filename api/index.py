import fitz
import io
import os
from flask import Flask, request, send_file, render_template

app = Flask(__name__, template_folder="../templates")

PAGE_H = 792  # altura en puntos Letter

def y(y_pt):
    return PAGE_H - y_pt

@app.route("/procesar", methods=["POST"])
def procesar():
    doc = None
    try:
        # -------- DATOS --------
        nombre = request.form.get("nombre", "MARIANA MARTINEZ SOTELO").upper()
        rfc = request.form.get("rfc", "MASM980308217").upper()
        curp = request.form.get("curp", "MASM980308MMCRTR09").upper()
        idcif = request.form.get("idcif", "16040028836")
        fecha_inicio = request.form.get("fecha_inicio", "01 DE ABRIL DE 2016")

        cp = request.form.get("cp", "56704")
        vialidad = request.form.get("vialidad", "CALLE").upper()
        nombre_vialidad = request.form.get("nombre_vialidad", "LIMON").upper()
        n_ext = request.form.get("n_ext", "SN")
        colonia = request.form.get("colonia", "CENTRO").upper()
        municipio = request.form.get("municipio", "TLALMANALCO").upper()
        entidad = request.form.get("entidad", "MEXICO").upper()

        # -------- PDF BASE --------
        base = os.path.dirname(os.path.abspath(__file__))
        pdf_path = os.path.join(base, "CUPY620808MPLRRL07_LIMPIO.pdf")
        doc = fitz.open(pdf_path)
        page = doc[0]

        f_reg = "helv"
        f_bold = "hebo"

        # ================= CÉDULA SUPERIOR =================
        page.insert_textbox(
            fitz.Rect(80, y(650), 250, y(620)),
            rfc,
            fontsize=8,
            fontname=f_bold,
            align=1
        )

        page.insert_textbox(
            fitz.Rect(80, y(625), 250, y(600)),
            nombre,
            fontsize=6.5,
            fontname=f_reg,
            align=1
        )

        page.insert_textbox(
            fitz.Rect(80, y(605), 250, y(585)),
            f"idCIF: {idcif}",
            fontsize=6.5,
            fontname=f_reg,
            align=1
        )

        # ================= IDENTIFICACIÓN =================
        page.insert_text((255, y(452)), rfc, fontsize=7, fontname=f_reg)
        page.insert_text((255, y(428.5)), curp, fontsize=7, fontname=f_reg)
        page.insert_text((255, y(405)), nombre, fontsize=7, fontname=f_reg)
        page.insert_text((255, y(381.5)), fecha_inicio, fontsize=7, fontname=f_reg)
        page.insert_text((255, y(358)), "ACTIVO", fontsize=7, fontname=f_reg)

        # ================= DOMICILIO =================
        page.insert_text((255, y(293)), cp, fontsize=7, fontname=f_reg)
        page.insert_text((440, y(293)), vialidad, fontsize=7, fontname=f_reg)

        page.insert_text((255, y(270)), nombre_vialidad, fontsize=7, fontname=f_reg)
        page.insert_text((440, y(270)), n_ext, fontsize=7, fontname=f_reg)

        page.insert_text((255, y(246.5)), colonia, fontsize=7, fontname=f_reg)
        page.insert_text((255, y(223)), municipio, fontsize=7, fontname=f_reg)
        page.insert_text((255, y(199.5)), entidad, fontsize=7, fontname=f_reg)

        # -------- SALIDA --------
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
        return f"Error: {str(e)}", 500
    finally:
        if doc:
            doc.close()

@app.route("/")
def home():
    return render_template("index.html")
