from avalon_scraper.utils import normalize_url, slugify

BASE = "https://avalon.law.yale.edu/"


def test_normalize_url_join():
    parent = BASE + "subject_menus/18th.asp"
    child = normalize_url("../18th_century/fed_01.asp", parent)
    assert child.startswith(BASE)


def test_slugify():
    s = slugify("Virginia Declaration of Rights (1776)")
    assert s.startswith("Virginia-Declaration-of-Rights-1776")