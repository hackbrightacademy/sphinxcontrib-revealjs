from docutils import nodes
from docutils.nodes import Structural, Element, Invisible


class Slide(Structural, Element):
    pass


class interslide(Slide):
    pass


class newslide(Slide, Invisible):
    pass


class speakernote(Structural, Element):
    pass


def visit_interslide(self, node: nodes.Node) -> None:
    """Create a new slide.

    If the parent slide is a normal slide (i.e. it is not a title or sub-title
    slide), close it.

    This function should only be registered with the revealjs builder.
    """

    self._new_section(node)


def depart_interslide(self, node: nodes.Node) -> None:
    self.body.append("</section>\n")


def visit_speakernote(self, node: nodes.Node) -> None:
    classes = " ".join(node["classes"])
    self.body.append(f'<aside class="{classes}">')


def depart_speakernote(self, node: nodes.Node) -> None:
    self.body.append("</aside>\n")


def visit_newslide(self, node: nodes.Node) -> None:
    # Close previous section and start a new one.
    self.body.append("</section>")
    self._new_section(node)

    title_tagname = f"h{self.section_level}"
    self.body.append(
        f"<{title_tagname}>{node['localtitle']}</{title_tagname}>"
    )


def depart_newslide(self, node: nodes.Node) -> None:
    return None
