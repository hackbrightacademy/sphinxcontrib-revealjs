"""RevealJS extenstion for Sphinx."""

from docutils.nodes import Node

from os import path
from pathlib import Path

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.config import Config

from . import addnodes, builder, transforms

from .directives.slides import Interslide, Newslide
from .directives.incremental import Incremental
from .directives.speakernote import Speakernote


def ignore_node(self, node: Node) -> None:
    raise nodes.SkipNode


def setup(app: Sphinx) -> None:
    app.setup_extension("sphinx.builders.html")

    # Setup builder and transforms
    app.add_builder(builder.RevealJSBuilder)
    app.connect("doctree-read", transforms.migrate_transitions_to_newslides)
    app.connect("doctree-resolved", transforms.process_newslides)

    # Theme
    app.add_html_theme(
        "revealjs",
        (Path(builder.package_dir) / Path("theme")).resolve(),
    )

    # Config values
    app.add_config_value("revealjs_theme", "revealjs", "html")
    app.add_config_value(
        "revealjs_theme_options", {"revealjs_theme": "black.css"}, "html"
    )
    app.add_config_value("revealjs_break_on_transition", True, "html")
    app.add_config_value("revealjs_newslides_inherit_titles", True, "html")

    # Nodes
    app.add_node(
        addnodes.newslide,
        html=(ignore_node, None),
        revealjs=(addnodes.visit_newslide, addnodes.depart_newslide),
    )
    app.add_node(
        addnodes.interslide,
        html=(ignore_node, None),
        revealjs=(addnodes.visit_interslide, addnodes.depart_interslide),
    )
    app.add_node(
        addnodes.speakernote,
        html=(ignore_node, None),
        revealjs=(addnodes.visit_speakernote, addnodes.depart_speakernote),
    )

    # Directives
    app.add_directive("interslide", Interslide)
    app.add_directive("newslide", Newslide)
    app.add_directive("speaker", Speakernote)
    app.add_directive("incremental", Incremental)
    app.add_directive("incr", Incremental)
