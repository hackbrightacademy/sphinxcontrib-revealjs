import pytest
from bs4 import BeautifulSoup, element


def with_revealjs_interslide(*args, **kw):
    default_kw = {
        "buildername": "revealjs",
        "testroot": "interslide",
    }
    default_kw.update(kw)
    return pytest.mark.sphinx(*args, **default_kw)


@with_revealjs_interslide()
def test_interslide(content_soup):
    compare = BeautifulSoup(
        "".join(
            (
                '<section class="interslide section">',
                "<p>Interslide 1</p>",
                "</section>",
            )
        ),
        "html.parser",
    )
    interslide = content_soup.find("section", class_="interslide")
    assert interslide.prettify().strip() == compare.prettify().strip()


@with_revealjs_interslide()
def test_interslide_follows_section(content_soup):
    compare = BeautifulSoup(
        "".join(
            (
                "<section>",
                "<h1>Slide 1</h1>",
                "</section>",
            )
        ),
        "html.parser",
    )
    interslide = content_soup.find("section", class_="interslide")

    element_sibling = None
    for sibling in interslide.previous_siblings:
        if isinstance(sibling, element.Tag):
            element_sibling = sibling
            break

    assert element_sibling.prettify().strip() == compare.prettify().strip()
