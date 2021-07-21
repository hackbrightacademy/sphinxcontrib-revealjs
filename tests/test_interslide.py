import pytest


def with_revealjs_interslide(*args, **kw):
    default_kw = {
        "buildername": "revealjs",
        "testroot": "interslide",
    }
    default_kw.update(kw)
    return pytest.mark.sphinx(*args, **default_kw)


@with_revealjs_interslide()
def test_interslide(content_soup):
    assert len(content_soup.select(".interslide")) == 3


@with_revealjs_interslide()
def test_interslide_follows_previous_sibling(content_soup):
    for idx, el in enumerate(content_soup.select(".interslide")):
        el.previous_sibling.parent.find("section", id=True)[
            "id"
        ] == f"slide-{idx + 1}"
