import logging
from flask import Flask, request

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("FlaskService")

UPLOAD_FOLDER = "/data"

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/test")
def test():
    """
    Test endpoint to check if the system is up
    """
    return {"status": "running"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8080")
