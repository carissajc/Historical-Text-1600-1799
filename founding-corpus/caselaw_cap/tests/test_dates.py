from caselaw_cap.date_extract import parse_first_date, header_region


def test_month_day_year():
    h = "Supreme Court\nDecided January 5, 1799\n..."
    dm = parse_first_date(header_region(h))
    assert dm and dm.year == 1799


def test_month_year():
    h = "Court of Errors\nOctober 1797\n..."
    dm = parse_first_date(header_region(h))
    assert dm and dm.year == 1797


def test_decided_phrase():
    h = "Argued November 12, 1796. Decided 1797."
    dm = parse_first_date(header_region(h))
    assert dm and dm.year in (1796, 1797)


def test_term_year():
    h = "October Term, 1799\n..."
    dm = parse_first_date(header_region(h))
    assert dm and dm.year == 1799


def test_fallback_year():
    h = "HEADER\nSome case\n1795\nBODY"
    dm = parse_first_date(header_region(h))
    assert dm and dm.year == 1795

