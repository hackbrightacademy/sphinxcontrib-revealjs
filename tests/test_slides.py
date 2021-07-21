import pytest


def with_revealjs_slides(*args, **kw):
    default_kw = {
        "buildername": "revealjs",
        "testroot": "slides",
    }
    default_kw.update(kw)
    return pytest.mark.sphinx(*args, **default_kw)


@with_revealjs_slides()
def test_slides(content_soup):
    assert len(content_soup.select("section > section")) == 3
    assert len(content_soup.select(".slides > section")) == 2


@with_revealjs_slides()
def test_h1_slide(content_soup):
    assert content_soup.h1.parent["id"] == "index"
    assert content_soup.h1.parent.get_text().strip() == "Index"


@with_revealjs_slides()
def test_h2_slide(content_soup):
    assert content_soup.h2.parent["id"] == "heading-2"
    assert content_soup.h2.parent.get_text().strip() == "Heading 2"


@with_revealjs_slides()
def test_h3_slide(content_soup):
    assert content_soup.h3.parent["id"] == "heading-3"

    lines = [
        line.strip()
        for line in content_soup.h3.parent.get_text().splitlines()
        if line
    ]
    assert lines[0] == "Heading 3"
    assert lines[1] == "Contents"


@with_revealjs_slides(confoverrides={"revealjs_title_slides": [1, 2, 3]})
def test_title_slides_config(content_soup):
    assert len(content_soup.select("section > section")) == 3
    assert len(content_soup.select(".slides > section")) == 1
