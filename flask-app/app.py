import concurrent.futures
import logging
import os

import pdftotext
import regex
from flask import Flask, request
from werkzeug.utils import secure_filename

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("FlaskService")

UPLOAD_FOLDER = "/data"

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def is_pdf(filename):
    """
    Validates if a filename contains pdf extension

    Args:
        filename: filename to check

    Returns:
        validity of the filename
    """
    return "pdf" == filename.lower()[-3:]


@app.route("/test")
def test():
    """
    Test endpoint to check if the system is up
    """
    return {"status": "running"}


@app.route("/list")
def list_files():
    """
    List uploaded pdf files
    """
    folders = os.listdir(app.config["UPLOAD_FOLDER"])
    document_names = sorted([f for f in folders if is_pdf(f)])
    return {"files": document_names, "number_of_files": len(document_names)}


def pdf_to_text(doc):
    """
    Converts pdf file to txt file

    Args:
        doc: document path
    """
    doc_text = doc + ".txt"
    if not os.path.exists(doc_text):
        with open(doc, "rb") as f:
            pdf_reader = pdftotext.PDF(f)
        text = "".join(pdf_reader)
        with open(doc_text, "w") as f:
            f.write(text)
        os.chmod(doc_text, 0o777)


@app.route("/upload", methods=["PUT"])
def upload_file():
    """
    Endpoint to upload pdf file and convert to txt
    """
    if request.method == "PUT":
        # Check if the request has the file
        if "file" not in request.files or request.files["file"].filename == "":
            logger.info("File is not present in the request")
            return {"error": "file not found"}, 400
        file = request.files["file"]

        if not is_pdf(file.filename):
            return {"error": "Only pdf files are allowed"}, 415

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        # Change filename if that filename exists
        while os.path.exists(file_path):
            filename = "1_" + filename
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        file.save(file_path)

        # Change permission, otherwise I cannot process the file
        os.chmod(file_path, 0o777)

        # Convert to txt (searching txt is faster than searching pdf)
        pdf_to_text(file_path)
        return {"result": "File uploaded successfully!", "file_name": filename}


def search_file(pdf_path, word):
    """
    Search word in the given pdf path

    Args:
        pdf_path: path to the pdf file to search

    Returns:
        [
            number of exact matches,
            number of possible matches with more error tolerance,
            path to the pdf file searched
        ]
    """
    txt_path = pdf_path + ".txt"
    with open(txt_path, "r") as f:
        txt_reader = f.readlines()
    text = "".join(txt_reader)

    # Error tolerance up to 3 characters for possible match
    possible_match_reg = r"(%s){e<=3}" % word
    if len(word) < 6:
        # if the word is shorter, error tolerance is also shorter
        possible_match_reg = r"(%s){e<=1}" % word
    possible_match = regex.findall(
        possible_match_reg, text, flags=regex.IGNORECASE | regex.BESTMATCH
    )
    # No error tolerance for exact match
    exact_match = regex.findall(
        r"%s" % word, text, flags=regex.IGNORECASE | regex.BESTMATCH
    )
    return [len(exact_match), len(possible_match), pdf_path]


@app.route("/search", methods=["POST"])
def search_documents():
    """
    Endpoint to search a word in the valid documents uploaded
    """
    if request.method == "POST":
        word = request.form.get("word")
        if len(word) < 4:
            return {"error": "Word is too short. Use at least 4 letters"}, 400

        all_files = list_files()["files"]
        futures = []
        # Decrease response time by adding concurrency
        with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
            for filename in all_files:
                doc = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                future = executor.submit(search_file, doc, word)
                futures.append(future)

        matches = []
        # get results of the futures async
        for future in concurrent.futures.as_completed(futures):
            exact, possible, doc = future.result()
            matches.append([exact, possible, doc])

        # Sort based on exact match and then possible match
        matches.sort(key=lambda x: (-x[0], -x[1]))
        return {
            "word": word,
            "result": [
                {
                    "file_name": match[2],
                    "exact_match": match[0],
                    "possible_match": match[1],
                }
                for match in matches[:3]
            ],
        }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8080")
