import logging
import os

import pdftotext
from flask import Flask, request
from werkzeug.utils import secure_filename

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("FlaskService")

UPLOAD_FOLDER = "/data"

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def is_pdf(filename):
    return "pdf" == filename.lower()[-3:]


@app.route("/test")
def test():
    """
    Test endpoint to check if the system is up
    """
    return {"status": "running"}


@app.route("/list_files")
def list_files():
    folders = os.listdir(app.config["UPLOAD_FOLDER"])
    document_names = sorted([f for f in folders if is_pdf(f)])
    return {"files": document_names}


def pdf_to_text(doc):
    doc_text = doc + ".txt"
    if not os.path.exists(doc_text):
        with open(doc, "rb") as f:
            pdf_reader = pdftotext.PDF(f)
        text = "".join(pdf_reader)
        with open(doc_text, "w") as f:
            f.write(text)


@app.route("/upload_file", methods=["POST"])
def upload_file():
    if request.method == "POST":
        file = request.files["file"]
        if not is_pdf(file.filename):
            return {"error": "Only pdf files are allowed"}, 415

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)
        pdf_to_text(file_path)
        return {"result": "File uploaded successfully!", "file_name": filename}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8080")
