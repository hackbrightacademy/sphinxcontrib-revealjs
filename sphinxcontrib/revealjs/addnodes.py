from docutils import nodes
from docutils.nodes import Structural, Element, Invisible


class Slide(Structural, Element):
    pass


class interslide(Slide):
    pass


class newslide(Invisible, Element):
    pass


class speakernote(Structural, Element):
    pass


def visit_interslide(self, node: nodes.Node) -> None:
    """Create a new slide.

    If the parent slide is a normal slide (i.e. it is not a title or sub-title
    slide), close it.

    This function should only be registered with the revealjs builder.
    """

    if self.section_level > 2:
        self.body.append("</section>\n")

    self._new_section(node)


def depart_interslide(self, node: nodes.Node) -> None:
    """Only close the slide if we're a top-level interslide."""

    if self.section_level == 2:
        self.body.append("</section>\n")


def visit_speakernote(self, node: nodes.Node) -> None:
    classes = " ".join(node["classes"])
    self.body.append(f'<aside class="{classes}">')


def depart_speakernote(self, node: nodes.Node) -> None:
    self.body.append("</aside>\n")