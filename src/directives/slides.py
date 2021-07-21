"""sphinxcontrib.revealjs.directives.slides"""

from typing import List
from docutils.nodes import Node
from sphinx.application import Sphinx

from docutils import nodes
from docutils.parsers.rst import directives

from sphinx.util.docutils import SphinxDirective
from sphinx.util.typing import OptionSpec

from . import optional_csscolorvalue, optional_uri

REVEALJS_TRANSITIONS = [  # see: https://revealjs.com/transitions/#styles
    "none",
    "fade",
    "slide",
    "convex",
    "concave",
    "zoom",
]
REVEALJS_TRANSITION_SPEEDS = [  # see: https://revealjs.com/transitions/
    "default",
    "fast",
    "slow",
]


def optional_revealjstransition(argument: str) -> str:
    return directives.choice(argument, REVEALJS_TRANSITIONS)


def optional_revealjstransitionspeed(argument: str) -> str:
    return directives.choice(argument, REVEALJS_TRANSITION_SPEEDS)


class BaseSlide(SphinxDirective):
    """Base for slide directives."""

    option_spec: OptionSpec = {
        "class": directives.class_option,
        "background-color": optional_csscolorvalue,
        "background-image": optional_uri,
        "transition": optional_revealjstransition,
        "transition-speed": optional_revealjstransitionspeed,
    }

    def options2atts(self, node: Node) -> None:
        """Set ``self.options`` as RevealJS-compatible attributes on ``node``."""

        node["classes"] += self.options.get("class", [])

        bg_color = self.options.get("background-color")
        if bg_color:
            node["data-background-color"] = bg_color

        bg_image = self.options.get("background-image")
        if bg_image:
            node["data-background-image"] = bg_image

        transition = self.options.get("transition")
        if transition:
            node["data-transition"] = transition

        transition_speed = self.options.get("transition-speed")
        if transition_speed:
            node["data-transition-speed"] = transition_speed


class interslide(nodes.General, nodes.Element):
    pass


class Interslide(BaseSlide):
    """An interstitial slide.

    Only displayed when using revealjs builder.
    """

    has_content = True
    required_arguments = 0
    optional_arguments = 1

    def run(self) -> List[Node]:
        slide_node = interslide(
            "\n".join(self.content), classes=["interslide"]
        )

        self.options2atts(slide_node)

        if self.arguments:
            slide_node.insert(0, nodes.title(text=self.arguments[0]))

        self.add_name(slide_node)
        self.set_source_info(slide_node)
        self.state.nested_parse(self.content, self.content_offset, slide_node)

        return [slide_node]


def visit_interslide(self, node: Node) -> None:
    """Create a new slide.

    If the parent slide is a normal slide (i.e. it is not a title or sub-title
    slide), close it.

    This function should only be registered with the revealjs builder.
    """

    if self.section_level > 2:
        self.body.append("</section>")

    self._new_section(node)


def depart_interslide(self, node: Node) -> None:
    """Only close the slide if we're a top-level interslide."""

    if self.section_level == 2:
        self.body.append("</section>")


def ignore_interslide(self, node: Node) -> None:
    raise nodes.SkipNode


def setup(app: Sphinx) -> None:
    app.add_node(
        interslide,
        html=(ignore_interslide, None),  # type: ignore
        handouts=(ignore_interslide, None),  # type: ignore
        revealjs=(visit_interslide, depart_interslide),
    )
    app.add_directive("interslide", Interslide)
