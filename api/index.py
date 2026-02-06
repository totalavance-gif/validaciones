import fitz
import io
import os
from datetime import datetime
from flask import Flask, request, send_file, render_template

app = Flask(__name__, template_folder="../templates")

PAGE_H = 792
OFFSET_X = 8     
OFFSET_Y = -6    

def y(pt):
    return PAGE_H - pt + OFFSET_Y

def x(pt):
    return pt + OFFSET_X

@app.route("/procesar", methods=["POST"])
def procesar():
    doc = None
    try:
        # ====== DATOS EXTRAÍDOS SEGÚN FORMATO SAT ======
        # Se ajustaron los nombres para que coincidan con la terminología oficial
        data = {
            "rfc": request.form.get("rfc", "MASM980308217").upper(),
            "curp": request.form.get("curp", "MASM980308MMCRTR09").upper(),
            "nombre": request.form.get("nombre", "MARIANA MARTINEZ SOTELO").upper(),
            "idcif": request.form.get("idcif", "16040028836"),
            "estatus": "ACTIVO",
            "fecha_ini": request.form.get("fecha_ini", "01 DE ABRIL DE 2016"),
            "cp": request.form.get("cp", "56704"),
            "vialidad": request.form.get("vialidad", "CALLE").upper(),
            "nombre_vialidad": request.form.get("nombre_vialidad", "LIMON").upper(),
            "n_ext": request.form.get("n_ext", "SN"),
            "colonia": request.form.get("colonia", "CENTRO").upper(),
            "municipio": request.form.get("municipio", "TLALMANALCO").upper(),
            "entidad": request.form.get("entidad", "MEXICO").upper(),
            "actividad": request.form.get("actividad", "Asalariado").upper(),
            "porcentaje": "100",
            "regimen": request.form.get("regimen", "Régimen de Sueldos y Salarios e Ingresos Asimilados a Salarios").upper()
        }

        # Fecha de emisión automática o manual
        lugar_fecha = f"{data['municipio']}, {data['entidad']} A {datetime.now().day} DE ENERO DE 2026"

        base = os.path.dirname(os.path.abspath(__file__))
        pdf_path = os.path.join(base, "CUPY620808MPLRRL07_LIMPIO.pdf")
        doc = fitz.open(pdf_path)

        # ================== PÁGINA 1 ==================
        page = doc[0]

        # ---- BLOQUE SUPERIOR (CÉDULA DE IDENTIFICACIÓN FISCAL) ----
        # RFC en Cédula
        page.insert_textbox(
            fitz.Rect(x(80), y(650), x(260), y(620)),
            data['rfc'], # Solo el RFC sin etiquetas adicionales
            fontsize=8,
            fontname="hebo",
            align=1
        )

        page.insert_textbox(
            fitz.Rect(x(80), y(625), x(260), y(600)),
            data["nombre"],
            fontsize=6.5,
            fontname="helv",
            align=1
        )

        page.insert_textbox(
            fitz.Rect(x(80), y(605), x(260), y(585)),
            f"idCIF: {data['idcif']}", # Nombre oficial: idCIF
            fontsize=6.5,
            fontname="helv",
            align=1
        )

        # Lugar y Fecha de Emisión
        page.insert_text((x(310), y(648)), lugar_fecha, fontsize=7, fontname="hebo")

        # ---- DATOS DE IDENTIFICACIÓN DEL CONTRIBUYENTE ----
        page.insert_text((x(255), y(452)), data["rfc"], fontsize=7)
        page.insert_text((x(255), y(428)), data["curp"], fontsize=7)
        page.insert_text((x(255), y(404)), data["nombre"], fontsize=7)
        page.insert_text((x(255), y(381)), data["fecha_ini"], fontsize=7)
        page.insert_text((x(255), y(358)), data["estatus"], fontsize=7)

        # ---- DATOS DEL DOMICILIO REGISTRADO ----
        page.insert_text((x(255), y(293)), data["cp"], fontsize=7)
        page.insert_text((x(440), y(293)), data["vialidad"], fontsize=7)

        page.insert_text((x(255), y(270)), data["nombre_vialidad"], fontsize=7)
        page.insert_text((x(440), y(270)), data["n_ext"], fontsize=7)

        page.insert_text((x(255), y(246)), data["colonia"], fontsize=7)
        page.insert_text((x(255), y(223)), data["municipio"], fontsize=7)
        page.insert_text((x(255), y(199)), data["entidad"], fontsize=7)

        # ================== PÁGINA 2 ==================
        page2 = doc[1]

        # Actividades Económicas
        page2.insert_text((x(45), y(615)), "1", fontsize=7)
        page2.insert_text((x(90), y(615)), data["actividad"], fontsize=7)
        page2.insert_text((x(415), y(615)), data["porcentaje"], fontsize=7)
        page2.insert_text((x(485), y(615)), "01/04/2016", fontsize=7) # Fecha inicio ejemplo

        # Regímenes
        page2.insert_textbox(
            fitz.Rect(x(60), y(540), x(450), y(510)),
            data["regimen"],
            fontsize=7,
            fontname="helv",
            align=0
        )
        page2.insert_text((x(485), y(530)), "01/04/2016", fontsize=7)

        # ====== SALIDA ======
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        return send_file(
            buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"CONSTANCIA_{data['rfc']}.pdf"
        )

    except Exception as e:
        return f"Error: {str(e)}", 500
    finally:
        if doc:
            doc.close()

@app.route("/")
def home():
    return render_template("index.html")
