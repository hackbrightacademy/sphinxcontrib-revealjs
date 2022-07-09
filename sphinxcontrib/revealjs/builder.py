"""RevealJS builder.

The builder is used with transforms to convert default Sphinx HTML output to
RevealJS-compatible HTML.
"""

from typing import Dict, Any, Tuple, List, Optional
from os import path
from textwrap import dedent

from docutils import nodes
from sphinx.util import logging, progress_message
from sphinx.util.fileutil import copy_asset
from sphinx.util.osutil import copyfile, ensuredir
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.writers.html5 import HTML5Translator

IMG_EXTENSIONS = ["jpg", "png", "gif", "svg"]

logger = logging.getLogger(__name__)
package_dir = path.abspath(path.dirname(__file__))


class RevealJSTranslator(HTML5Translator):
    """Translator for writing RevealJS slides."""

    _dl_fragment = 0
    section_level = 1

    def _new_section(
        self,
        node: nodes.Node,
        tagname: str = "section",
        classes_override: Optional[List[str]] = None,
    ) -> None:
        """Add a new section.

        In RevealJS, a new section is a new slide.
        """

        self.body.append(
            self.starttag(
                node,
                tagname,
                CLASS=" ".join(
                    classes_override or (node["classes"] + ["section"])
                ),
                **{
                    attr: val
                    for attr, val in node.attributes.items()
                    if attr.startswith("data-")
                },
            )
        )

    def visit_section(self, node: nodes.Node) -> None:
        """Only add a new section for 2nd- or 3rd-level sections."""

        self.section_level += 1

        if self.section_level in [2, 3]:
            self._new_section(node)

    def depart_section(self, node: nodes.Node) -> None:
        self.section_level -= 1

        if self.section_level in [1, 2]:
            self.body.append("</section>")

    def visit_title(self, node: nodes.Node) -> None:
        if self.section_level in [1, 2]:
            self.body.append("<section>")

        super().visit_title(node)

    def depart_title(self, node: nodes.Node) -> None:
        super().depart_title(node)

        if self.section_level in [1, 2]:
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
    search = False

    revealjs_dist = path.join(package_dir, "lib/revealjs/dist")
    revealjs_plugindir = path.join(package_dir, "lib/revealjs/plugin")

    def get_theme_config(self) -> Tuple[str, Dict]:
        """Override get_theme_config to return the theme config for RevealJS."""

        return (
            self.config.revealjs_theme,
            self.config.revealjs_theme_options,
        )

    def init_js_files(self) -> None:
        """Register names of RevealJS JS dependencies."""

        super().init_js_files()

        self.add_js_file("reveal.js", priority=500)
        self.add_js_file("plugin/notes/notes.js", priority=500)
        self.add_js_file(
            None,
            body=dedent(
                """
                Reveal.initialize({
                  hash: true,
                  plugins: [RevealNotes]
                });
            """
            ),
            priority=500,
        )

    def init_css_files(self) -> None:
        """Register names of RevealJS CSS dependencies.

        See: https://github.com/hakimel/reveal.js/blob/6b535328c0a9615c9cf4759acf81cd02f0516ba1/index.html#L9-L11
        """

        super().init_css_files()

        self.add_css_file("reset.css", priority=500)
        self.add_css_file("reveal.css", priority=500)

        if self.theme:
            _, theme_opts = self.get_theme_config()
            self.add_css_file(theme_opts["revealjs_theme"], priority=500)

    def copy_static_files(self) -> None:
        """Copy RevealJS static files to the output directory."""

        try:
            with progress_message("copying static files"):
                ensuredir(path.join(self.outdir, "_static"))
                self.copy_revealjs_files()
                self.copy_revealjs_plugin()
                self.copy_revealjs_theme()
        except OSError as err:
            logger.warning("cannot copy static file %r", err)

        super().copy_static_files()

    def copy_revealjs_files(self) -> None:
        copyfile(
            path.join(self.revealjs_dist, "reveal.css"),
            path.join(self.outdir, "_static", "reveal.css"),
        )
        copyfile(
            path.join(self.revealjs_dist, "reset.css"),
            path.join(self.outdir, "_static", "reset.css"),
        )
        copyfile(
            path.join(self.revealjs_dist, "reveal.js"),
            path.join(self.outdir, "_static", "reveal.js"),
        )

    def copy_revealjs_plugin(self) -> None:
        copy_asset(
            path.join(self.revealjs_plugindir, "notes"),
            path.join(self.outdir, "_static", "plugin", "notes"),
        )

    def copy_revealjs_theme(self) -> None:
        if self.theme:
            _, theme_opts = self.get_theme_config()
            revealjs_theme = theme_opts["revealjs_theme"]

            copyfile(
                path.join(self.revealjs_dist, "theme", revealjs_theme),
                path.join(self.outdir, "_static", revealjs_theme),
            )
