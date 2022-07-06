import re
from itertools import chain, cycle

from html5lib import HTMLParser
import pytest

etree_cache = {}


def flat_dict(d):
    # Code below is copied from https://github.com/sphinx-doc/sphinx/blob/9e1b4a8f1678e26670d34765e74edf3a3be3c62c/tests/test_build_html.py

    return chain.from_iterable(
        [zip(cycle([fname]), values) for fname, values in d.items()]
    )


@pytest.mark.sphinx(buildername="revealjs", testroot="builder-revealjs")
def test_revealjs_build(app):
    app.build()

    assert (app.outdir / "index.html").exists()

    assert (app.outdir / "_static/reset.css").exists()
    assert (app.outdir / "_static/reveal.css").exists()
    assert (app.outdir / "_static/reveal.js").exists()


@pytest.mark.sphinx(buildername="revealjs", testroot="builder-revealjs")
def test_revealjs_theme_css(app):
    default_theme = app.config.revealjs_theme_options[
        "revealjs_theme"
    ] = "simple.css"

    app.build()

    assert (app.outdir / "_static" / default_theme).exists()


@pytest.mark.sphinx(
    buildername="revealjs",
    testroot="builder-revealjs",
    confoverrides={
        "revealjs_theme_options": {"revealjs_theme": "solarized.css"}
    },
)
def test_revealjs_theme_css_override(app):
    app.build()

    assert (app.outdir / "_static" / "solarized.css").exists()


@pytest.mark.parametrize(
    "filename",
    ["notes/notes.js", "notes/plugin.js", "notes/speaker-view.html"],
)
@pytest.mark.sphinx(buildername="revealjs", testroot="builder-revealjs")
def test_revealjs_plugin_files(app, filename):
    app.build()

    assert (app.outdir / "_static/plugin" / filename).exists()


@pytest.mark.parametrize(
    "fname,expect",
    flat_dict(
        {
            "index.html": [
                (".//*[@class='admonition']", ""),
                (".//*[@class='sidebar']", ""),
                (".//*[@class='topic']", ""),
            ]
        }
    ),
)
@pytest.mark.sphinx(buildername="revealjs", testroot="builder-revealjs")
def test_revealjs_translator(app, cached_etree_parse, fname, expect):
    app.build()

    with pytest.raises(AssertionError):
        check_xpath(cached_etree_parse(app.outdir / fname), fname, *expect)


@pytest.mark.parametrize(
    "fname,expect",
    flat_dict(
        {
            "index.html": [
                (
                    ".//div[@class='slides']/section[2]/section[2]/h4",
                    "Heading 4",
                    True,
                ),
            ]
        }
    ),
)
@pytest.mark.sphinx(buildername="revealjs", testroot="builder-revealjs")
def test_revealjs_autobreak_slides(app, cached_etree_parse, fname, expect):
    app.build()

    check_xpath(cached_etree_parse(app.outdir / fname), fname, *expect)


@pytest.mark.parametrize(
    "fname,expect",
    flat_dict(
        {
            "index.html": [
                (
                    ".//div[@class='slides']/section[1]/section/h1",
                    "Index",
                    True,
                ),
                (
                    ".//div[@class='slides']/section[2]/section[1]/h2",
                    "Heading 2",
                    True,
                ),
                (
                    ".//div[@class='slides']/section/section[2]/h3",
                    "Heading 3",
                    True,
                ),
            ]
        }
    ),
)
@pytest.mark.sphinx(buildername="revealjs", testroot="builder-revealjs")
def test_revealjs_build_vertical_slides(
    app, cached_etree_parse, fname, expect
):
    app.build()

    check_xpath(cached_etree_parse(app.outdir / fname), fname, *expect)


@pytest.mark.parametrize(
    "fname,expect",
    flat_dict(
        {
            "index.html": [
                (
                    ".//div[@class='slides']/section[1]/h1",
                    "Index",
                    True,
                ),
                (
                    ".//div[@class='slides']/section[2]/h2",
                    "Heading 2",
                    True,
                ),
                (
                    ".//div[@class='slides']/section[3]/h3",
                    "Heading 3",
                    True,
                ),
            ]
        }
    ),
)
@pytest.mark.sphinx(buildername="revealjs", testroot="revealjs-conf")
def test_revealjs_build_no_vertical_slides(
    app, cached_etree_parse, fname, expect
):
    app.build()

    check_xpath(cached_etree_parse(app.outdir / fname), fname, *expect)


# Code below is copied from https://github.com/sphinx-doc/sphinx/blob/9e1b4a8f1678e26670d34765e74edf3a3be3c62c/tests/test_build_html.py


@pytest.fixture(scope="module")
def cached_etree_parse():
    def parse(fname):
        if fname in etree_cache:
            return etree_cache[fname]
        with (fname).open("rb") as fp:
            etree = HTMLParser(namespaceHTMLElements=False).parse(fp)
            etree_cache.clear()
            etree_cache[fname] = etree
            return etree

    yield parse
    etree_cache.clear()


def tail_check(check):
    rex = re.compile(check)

    def checker(nodes):
        for node in nodes:
            if node.tail and rex.search(node.tail):
                return True
        assert False, "%r not found in tail of any nodes %s" % (check, nodes)

    return checker


def check_xpath(etree, fname, path, check, be_found=True):
    nodes = list(etree.findall(path))
    if check is None:
        assert (
            nodes == []
        ), "found any nodes matching xpath " "%r in file %s" % (path, fname)
        return
    else:
        assert (
            nodes != []
        ), "did not find any node matching xpath " "%r in file %s" % (
            path,
            fname,
        )
    if hasattr(check, "__call__"):
        check(nodes)
    elif not check:
        # only check for node presence
        pass
    else:

        def get_text(node):
            if node.text is not None:
                # the node has only one text
                return node.text
            else:
                # the node has tags and text; gather texts just under the node
                return "".join(n.tail or "" for n in node)

        rex = re.compile(check)
        if be_found:
            if any(rex.search(get_text(node)) for node in nodes):
                return
        else:
            if all(not rex.search(get_text(node)) for node in nodes):
                return

        assert (
            False
        ), "%r not found in any node matching " "path %s in %s: %r" % (
            check,
            path,
            fname,
            [node.text for node in nodes],
        )
