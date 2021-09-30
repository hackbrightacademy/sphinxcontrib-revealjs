import pytest


@pytest.mark.sphinx(buildername="revealjs", testroot="builder-revealjs")
def test_revealjs_build(app):
    app.build()

    assert (app.outdir / "index.html").exists()

    assert (app.outdir / "_static/reset.css").exists()
    assert (app.outdir / "_static/reveal.css").exists()
    assert (app.outdir / "_static/reveal.js").exists()


@pytest.mark.sphinx(buildername="revealjs", testroot="builder-revealjs")
def test_revealjs_theme_css(app):
    default_theme = "simple.css"

    assert (app.outdir / "_static" / default_theme).exists()


@pytest.mark.parametrize(
    "filename",
    ["notes/notes.js", "notes/plugin.js", "notes/speaker-view.html"],
)
@pytest.mark.sphinx(buildername="revealjs", testroot="builder-revealjs")
def test_revealjs_plugin_files(app, filename):
    app.build()

    assert (app.outdir / "_static/plugin" / filename).exists()
