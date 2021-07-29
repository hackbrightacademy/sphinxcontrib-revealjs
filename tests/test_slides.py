"""Test that slides are created properly.

Title slides + automatic slide breaks.
"""

from bs4 import BeautifulSoup

import pytest


def with_revealjs_slides(*args, **kw):
    default_kw = {
        "buildername": "revealjs",
        "testroot": "slides",
    }
    default_kw.update(kw)
    return pytest.mark.sphinx(*args, **default_kw)


@with_revealjs_slides()
def test_slides(content_soup: BeautifulSoup):
    assert len(content_soup.select("section > section")) == 2
    assert len(content_soup.select(".slides > section")) == 2


@with_revealjs_slides()
def test_h1_slide(content_soup: BeautifulSoup):
    title_slide = content_soup.select(".reveal > .slides > section")[0]

    assert len(list(title_slide.children)) == 3
    assert title_slide.find("h1").get_text().strip() == "Index"


@with_revealjs_slides()
def test_h2_slide(content_soup: BeautifulSoup):
    section2 = content_soup.select("#heading-2")[0]
    section2_title_slide = section2.find("section")

    assert len(list(section2_title_slide.children)) == 3
    assert section2_title_slide.find("h2").get_text().strip() == "Heading 2"


@with_revealjs_slides()
def test_h3_slide(content_soup: BeautifulSoup):
    assert content_soup.h3.parent["id"] == "heading-3"

    lines = [
        line.strip()
        for line in content_soup.h3.parent.get_text().splitlines()
        if line
    ]
    assert lines[0] == "Heading 3"
    assert lines[1] == "Contents"
