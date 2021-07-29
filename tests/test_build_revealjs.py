import pytest


@pytest.mark.sphinx(buildername="revealjs", testroot="builder-revealjs")
def test_revealjs_build(app):
    app.build()

    assert (app.outdir / "index.html").exists()

    assert (app.outdir / "_static/reveal.css").exists()
    assert (app.outdir / "_static/reveal.js").exists()
    assert (app.outdir / "_static/simple.css").exists()
