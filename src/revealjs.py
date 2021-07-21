"""Sphinx writer for slides."""

from typing import Dict, Any, Tuple
from sphinx.application import Sphinx
from docutils import nodes

from os import path
from pathlib import PurePath

from sphinx.locale import __
from sphinx.util import logging
from sphinx.util.fileutil import copy_asset
from sphinx.util.matching import DOTFILES
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.writers.html5 import HTML5Translator

IMG_EXTENSIONS = ["jpg", "png", "gif", "svg"]

logger = logging.getLogger(__name__)


def get_attrs_as_html(node_attrs: Dict[str, Any]):
    """Convert docutil node attributes to HTML data- attributes."""

    basic_attrs = set(nodes.section.basic_attributes)

    html_attrs = {}
    for attr, val in node_attrs.items():
        if attr not in basic_attrs and type(val) is str:
            attr_name = f"data-{attr}" if attr != "class" else attr
            html_attrs[attr_name] = val
    return html_attrs


class RevealJSTranslator(HTML5Translator):
    """Translator for writing RevealJS slides."""

    permalink_text = False
    _dl_fragment = 0
    section_level = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.builder.add_permalinks = False

    def _add_path_to_builder(self, name: str, path: str) -> None:
        """Add path to a resource to builder."""

        parsed_path = PurePath(path.lower())
        if parsed_path.suffix in [f".{ext}" for ext in IMG_EXTENSIONS]:
            self.builder.images[name] = parsed_path.name

    def _new_section(self, node: nodes.Node) -> None:
        """Add a new section.

        In RevealJS, a new section is a new slide.
        """

        data_atts = {
            att: val
            for att, val in node.attributes.items()
            if att.startswith("data-")
        }

        # html_attrs = get_attrs_as_html(node.attributes)

        # if "data-background" in html_attrs:
        #     bg_name = node.attributes["background"]
        #     self._add_path_to_builder(bg_name, html_attrs["data-background"])
        #     if bg_name in self.builder.images:
        #         html_attrs["data-background"] = path.join(
        #             self.builder.imagedir, self.builder.images[bg_name]
        #         )

        self.body.append(
            self.starttag(node, "section", CLASS="section", **data_atts)
        )

    def visit_section(self, node: nodes.Node) -> None:
        """Only add a new section for 2nd- or 3rd-level sections."""

        self.section_level = node.get("depth", self.section_level) or 1
        self._new_section(node)

    def depart_section(self, node: nodes.Node) -> None:
        self.body.append("</section>")

    def visit_admonition(self, *args):
        raise nodes.SkipNode

    def visit_sidebar(self, node: nodes.Node) -> None:
        raise nodes.SkipNode

    def visit_topic(self, node: nodes.Node) -> None:
        raise nodes.SkipNode


class RevealJSBuilder(StandaloneHTMLBuilder):
    """Builder for making RevealJS using Sphinx."""

    name = "revealjs"
    default_translator_class = RevealJSTranslator

    def init(self) -> None:
        super().init()

        self.add_permalinks = self.get_builder_config("permalinks")
        self.search = self.get_builder_config("search")

    def get_builder_config(self, *args) -> Any:
        if len(args) == 1:
            return super().get_builder_config(args[0], "revealjs")
        else:
            return super().get_builder_config(*args)

    def get_theme_config(self) -> Tuple[str, Dict]:
        return (
            self.env.config.revealjs_theme,
            self.config.revealjs_theme_options,
        )

    def copy_revealjs_theme(self) -> None:
        def onerror(filename: str, error: Exception) -> None:
            logger.warning(
                __("Failed to copy a file in html_static_file: %s: %r"),
                filename,
                error,
            )

        if self.theme:
            _, theme_opts = self.get_theme_config()
            for entry in self.theme.get_theme_dirs()[::-1]:
                copy_asset(
                    path.join(
                        entry,
                        f'revealjs_themes/{theme_opts["revealjs_theme"]}.css',
                    ),
                    path.join(self.outdir, "_static"),
                    excluded=DOTFILES,
                    onerror=onerror,
                )

    def finish(self) -> None:
        self.finish_tasks.add_task(self.copy_revealjs_theme)
        return super().finish()


def setup(app: Sphinx) -> None:
    app.add_builder(RevealJSBuilder)
    app.add_config_value("revealjs_permalinks", False, "html")
    app.add_config_value("revealjs_search", False, "html")

    app.add_config_value("revealjs_theme", "revealjs", "html")
    app.add_config_value(
        "revealjs_theme_options", {"revealjs_theme": "simple"}, "html"
    )
