"""RevealJS extenstion for Sphinx."""

from pathlib import Path
from sphinx.application import Sphinx

from .directives import slides
from . import incremental, newslide, speakernote, revealjs, transforms


def setup(app: Sphinx) -> None:
    transforms.setup(app)
    incremental.setup(app)
    slides.setup(app)
    newslide.setup(app)
    speakernote.setup(app)
    revealjs.setup(app)
    app.add_html_theme(
        "revealjs",
        (Path(__file__).parent / Path("theme")).resolve(),
    )
