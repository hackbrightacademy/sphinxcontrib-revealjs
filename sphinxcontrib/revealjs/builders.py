"""Sphinx writer for slides."""

from typing import Dict, Any, Tuple, List
from sphinx.application import Sphinx
from docutils import nodes
from bs4.element import Tag

from os import path
from pathlib import PurePath, Path
from itertools import takewhile
from textwrap import dedent

from sphinx.locale import __
from sphinx.util import logging, progress_message
from sphinx.util.fileutil import copy_asset
from sphinx.util.osutil import copyfile, ensuredir
from sphinx.util.matching import DOTFILES, Matcher
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.writers.html5 import HTML5Translator

from sphinxcontrib.revealjs.soupbridge import SoupBridge, HEADING_TAGS

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

        if "data-background" in data_atts:
            bg_name = node.attributes["background"]
            self._add_path_to_builder(bg_name, data_atts["data-background"])
            if bg_name in self.builder.images:
                data_atts["data-background"] = path.join(
                    self.builder.imagedir, self.builder.images[bg_name]
                )

        self.body.append(
            self.starttag(node, "section", CLASS="section", **data_atts)
        )

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

    def copy_static_files(self) -> None:
        super().copy_static_files()

        try:
            with progress_message(__("copying static files")):
                self.copy_revealjs_files()
                self.copy_revealjs_plugin()
                self.copy_revealjs_theme()

                # This is hacky, but we need to call these methods again
                # so that users can override RevealJS files. Code here
                # is copied from sphinx.builders.html
                context = self.globalcontext.copy()
                if self.indexer is not None:
                    context.update(self.indexer.context_for_searchtool())
                self.copy_theme_static_files(context)
                self.copy_html_static_files(context)

        except OSError as err:
            logger.warning(__("cannot copy static file %r"), err)

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

    def init_js_files(self) -> None:
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
        super().init_css_files()

        self.add_css_file("reset.css", priority=500)
        self.add_css_file("reveal.css", priority=500)

        if self.theme:
            _, theme_opts = self.get_theme_config()
            self.add_css_file(
                theme_opts["revealjs_theme"],
                priority=500,
            )

    def mark_slide_depths(self):
        soup_bridge, soup = self.soup_bridge, self.soup_bridge.soup

        for slide in soup.select("div.slides section"):
            depth = soup_bridge.get_tag_depth(
                slide, stopwhen=lambda t: "slides" in t.get("class", [])
            )
            slide.attrs["data-depth"] = depth

    def unwrap_nested_slides(self):
        """Unwrap and flatten any nested slides.

        RevealJS turns <section> tags into slides.
        """

        soup = self.soup_bridge.soup

        slides_container = soup.new_tag("div", attrs={"class": "slides"})

        for slide in soup.select("div.slides section"):
            xslide = slide.extract()

            for child in takewhile(
                lambda child: child.name != "section", xslide.children
            ):
                xslide.append(child.extract())

            slides_container.append(xslide)

        soup.find("div", class_="slides").replace_with(slides_container)

    def handle_newslides(self):
        soup_bridge, soup = self.soup_bridge, self.soup_bridge.soup

        for newslide in soup.select(".newslide"):
            parent = newslide.parent

            newslide_container = soup_bridge.copy_tag(parent)
            del newslide_container["id"]  # Remove id
            newslide_container["class"] = "slide-break"
            newslide_container["data-slide-break-for"] = parent["id"]

            # Copy title
            parent_title = parent.find(lambda t: t.name in HEADING_TAGS)
            copied_title = soup.new_tag(parent_title.name)
            copied_title.string = soup.new_string(parent_title.string)
            newslide_container.append(copied_title)

            for sib in takewhile(
                lambda child: child.get("class") != "newslide"
                if type(child) is Tag
                else True,
                list(newslide.next_siblings),
            ):
                newslide_container.append(sib.extract())

            parent.insert_after(newslide_container)
            newslide.decompose()

    def handle_vertical_slides(self):
        soup = self.soup_bridge.soup

        for slide in soup.find_all(
            lambda tag: tag.get("data-depth") in (1, 2)
        ):
            wrapper = slide.wrap(soup.new_tag("section"))

            if slide.attrs["data-depth"] == 2:
                for inner_slide in takewhile(
                    lambda tag: tag.attrs["data-depth"] > 2,
                    list(wrapper.next_siblings),
                ):
                    wrapper.append(inner_slide.extract())

    def rewrite_html_for_revealjs(self):
        """Rearrange rendered HTML so it plays nice with RevealJS.

        We used to override visit/depart methods in RevealJSTranslator
        to accomplish what this method does but the logic got really
        *weird* and difficult to understand.

        This is an unconventional way to do things but it should be
        far more understandable and maintainable.
        """

        outfile = self.get_outfilename(self.current_docname)
        self.soup_bridge = SoupBridge(outfile)

        self.mark_slide_depths()
        self.unwrap_nested_slides()
        self.handle_newslides()
        if self.config.revealjs_vertical_slides:
            self.handle_vertical_slides()

        self.soup_bridge.write()

    def finish(self) -> None:
        self.finish_tasks.add_task(self.rewrite_html_for_revealjs)
        return super().finish()
