"""RevealJS extenstion for Sphinx."""

from docutils.nodes import Node

from os import path
from pathlib import Path
from sphinx.application import Sphinx

from docutils import nodes

from . import transforms, addnodes, builders

from .directives.slides import Interslide, Newslide
from .directives.incremental import Incremental
from .directives.speakernote import Speakernote


def ignore_node(self, node: Node) -> None:
    raise nodes.SkipNode


def setup(app: Sphinx) -> None:
    # Theme
    app.add_html_theme(
        "revealjs",
        (Path(builders.package_dir) / Path("theme")).resolve(),
    )

    app.add_js_file("reveal.js")

    # Config
    app.add_config_value("revealjs_permalinks", False, "html")
    app.add_config_value("revealjs_search", False, "html")
    app.add_config_value("revealjs_theme", "revealjs", "html")
    app.add_config_value(
        "revealjs_theme_options", {"revealjs_theme": "simple.css"}, "html"
    )
    app.add_config_value("revealjs_vertical_slides", True, "html")
    app.add_config_value("revealjs_break_on_transition", True, "html")

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

    # Transforms
    app.connect("doctree-read", transforms.migrate_transitions_to_newslides)

    # Builders
    app.add_builder(builders.RevealJSBuilder)
