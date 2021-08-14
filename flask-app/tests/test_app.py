import os

from .. import app


def test_test():
    """Test if the app is running"""
    assert app.test()["status"] == "running"


def test_is_pdf():
    """Test if is_pdf function works"""
    filename_1 = "test.pdf"
    filename_2 = "test.txt"
    assert app.is_pdf(filename_1) == True
    assert app.is_pdf(filename_2) == False


def test_list_files():
    """Tests if list_files function works"""
    files = app.list_files()
    assert type(files["files"]) == list
    assert len(files["files"]) == files["number_of_files"]


def test_pdf_to_text():
    """Tests if pdf_to_text function works"""
    pdf_path = "/test-data/test.pdf"
    txt_path = pdf_path + ".txt"
    true_txt_path = "/test-data/true_test.txt"

    app.pdf_to_text(pdf_path)

    # read the generated file
    with open(txt_path, "r") as f:
        txt_reader = f.readlines()
    text = "".join(txt_reader)

    # read the ground truth
    with open(true_txt_path, "r") as f:
        txt_reader = f.readlines()
    true_text = "".join(txt_reader)

    assert text == true_text

    # clean the folder
    os.remove(txt_path)


def test_search_file():
    """Tests if search_file function works"""
    pdf_path = "/test-data/test.pdf"
    txt_path = pdf_path + ".txt"
    app.pdf_to_text(pdf_path)
    words = [
        ("document", 11, 15),
        ("create", 5, 13),
        ("docker", 6, 20),
    ]
    for word, true_exact, true_possible in words:
        exact_match, possible_match, path = app.search_file(pdf_path, word)
        assert path == pdf_path
        assert exact_match == true_exact
        assert possible_match == true_possible

    # clean the folder
    os.remove(txt_path)
