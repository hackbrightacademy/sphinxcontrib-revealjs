"""Sphinx writer for slides."""

from typing import Dict, Any, Tuple, List, Optional
from docutils import nodes

from os import path
from textwrap import dedent

from sphinx.locale import __
from sphinx.util import logging, progress_message
from sphinx.util.fileutil import copy_asset
from sphinx.util.osutil import copyfile, ensuredir
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.writers.html5 import HTML5Translator

from bs4 import BeautifulSoup

IMG_EXTENSIONS = ["jpg", "png", "gif", "svg"]

logger = logging.getLogger(__name__)
package_dir = path.abspath(path.dirname(__file__))


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

    def visit_section(self, node):
        self.section_level = node.get("data-depth", 1)
        self._new_section(node)

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
    revealjs_dist = path.join(package_dir, "lib/revealjs/dist")
    revealjs_plugindir = path.join(package_dir, "lib/revealjs/plugin")

    def init(self) -> None:
        super().init()

        self.add_permalinks = self.get_builder_config("permalinks", "revealjs")
        self.search = self.get_builder_config("search", "revealjs")

    def get_theme_config(self) -> Tuple[str, Dict]:
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
        try:
            with progress_message(__("copying static files")):
                ensuredir(path.join(self.outdir, "_static"))
                self.copy_revealjs_files()
                self.copy_revealjs_plugin()
                self.copy_revealjs_theme()
        except OSError as err:
            logger.warning(__("cannot copy static file %r"), err)

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

    def write_vertical_slides(self):
        """Rearrange rendered HTML so it plays nice with RevealJS.

        We used to override visit/depart methods in RevealJSTranslator
        to accomplish what this method does but the logic got really
        *weird* and difficult to understand.

        This is an unconventional way to do things but it should be
        far more understandable and maintainable.

        h1 and h2 titles mark the beginning of each vertical stack
        of slides. We're basically doing this:

            h1     h2     h2     h2
                   h3     h3
                   h3     h3
                   h3
        """

        outfile = self.get_outfilename(self.current_docname)
        with open(outfile) as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        # Isolate title slides (section elements with depth 1)
        for slide in soup.find_all(lambda el: el.get("data-depth") == "1"):
            slide.wrap(soup.new_tag("section"))

        # Then, sections with h2 titles (equivalent to data-depth="2")
        # mark the beginning of their own vertical stacks.
        for slide in soup.find_all(lambda tag: tag.get("data-depth") == "2"):
            wrapper = slide.wrap(soup.new_tag("section"))

            # Add slides until we get to the next h2 section
            sib = next(wrapper.next_siblings)
            while True:
                if sib.get("data-depth") == "2":
                    break

                wrapper.append(sib.extract())

                try:
                    sib = next(wrapper.next_siblings)
                except StopIteration:
                    break

            # Clean up any nested sections. RevealJS gets buggy
            # when slides are nested more than 2 deep.
            for subsection in wrapper.find_all(
                lambda tag: int(tag.get("data-depth", 0)) > 3
            ):
                subsection.unwrap()

        with open(outfile, "w") as f:
            f.write(soup.prettify())

    def finish(self) -> None:
        if self.config.revealjs_vertical_slides:
            logger.info(__("Rewriting HTML to create vertical slides..."))
            self.finish_tasks.add_task(self.write_vertical_slides)

        return super().finish()
