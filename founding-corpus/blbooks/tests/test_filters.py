from blbooks.bl_loader import page_ok, lang_is_english
from blbooks.bl_assemble import assemble_books

def test_lang_filter():
    rec = {"Language_1": "English", "date": 1750, "text": "x", "empty_pg": False}
    assert lang_is_english(rec, ["English"]) is True
    rec2 = {"Language_1": "French", "Language_2": "ENGLISH", "date": 1750, "text": "x"}
    assert lang_is_english(rec2, ["English"]) is True


def test_page_ok():
    rec = {"Language_1": "English", "date": 1750, "text": "hello", "empty_pg": False}
    assert page_ok(rec, 1730, 1779, ["English"], True)
    rec2 = {"Language_1": "English", "date": 1800, "text": "hello", "empty_pg": False}
    assert page_ok(rec2, 1730, 1779, ["English"], True) is False


def test_assemble_order():
    pages = [
        {"record_id": "A", "pg": 2, "text": "Page2", "date": 1750},
        {"record_id": "A", "pg": 1, "text": "Page1", "date": 1750},
    ]
    out = list(assemble_books(pages))
    rid, doc = out[0]
    assert rid == "A"
    assert "Page1" in doc["text"] and doc["text"].find("Page1") < doc["text"].find("Page2")