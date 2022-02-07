"""sphinxcontrib.revealjs.transforms"""

from sphinx.application import Sphinx
from docutils import nodes
from sphinx.transforms.post_transforms import SphinxPostTransform

from . import addnodes


def get_node_depth(node: nodes.section) -> int:
    """Return depth of section, relative to document root."""

    depth = 1
    current = node
    while not isinstance(current.parent, nodes.document):
        depth += 1

        current = current.parent

    return depth


def migrate_transitions_to_newslides(
    app: Sphinx, doctree: nodes.document
) -> None:
    """Turn transition nodes into newslide nodes.

    This will only happen if the config value, `revealjs_break_on
    transition` is `True`.
    """

    if not app.config.revealjs_break_on_transition:
        return

    for node in doctree.traverse(nodes.transition):
        node.replace_self(addnodes.newslide("", localtitle=""))


class UnwrapSectionNodes(SphinxPostTransform):
    """We don't want to write nested sections."""

    default_priority = 900

    def mark_section_depths(self):
        for node in self.document.traverse(nodes.section):
            node["data-depth"] = get_node_depth(node)

    def mark_newslide_depths(self):
        for node in self.document.traverse(addnodes.newslide):
            node["data-depth"] = node.parent.get("data-depth", 1)

    def run(self) -> None:
        self.mark_section_depths()
        self.mark_newslide_depths()

        children = []
        for node in reversed(
            list(
                self.document.children[0].traverse(
                    lambda n: isinstance(n, nodes.section)
                    and n.get("data-depth") in self.config.revealjs_autobreak
                )
            )
        ):
            children.append(node.deepcopy())
            node.parent.remove(node)

        self.document.extend(reversed(children))


class AddNewslideTitles(SphinxPostTransform):
    """Add title nodes to newslides."""

    default_priority = 901

    def run(self) -> None:
        for node in self.document.traverse(addnodes.newslide):
            if not node["localtitle"]:
                # Copy title from parent
                title = node.parent[
                    node.parent.first_child_matching_class(nodes.title)
                ]
                node["localtitle"] = title.astext()
