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


def process_newslides(app: Sphinx, doctree: nodes.document, _) -> None:
    """Process newslides after doctree is resolved."""

    while doctree.traverse(addnodes.newslide):
        newslide_node = doctree.next_node(addnodes.newslide)
        if app.builder.name != "revealjs":
            newslide_node.parent.remove(newslide_node)
            continue

        parent_section = newslide_node.parent

        # parent_section might have been created by a newslide_node.
        # If so, traverse until we find a "real" slide.
        check_section = parent_section
        while "localtitle" in check_section.attributes:
            i = check_section.parent.index(check_section)
            check_section = check_section.parent.children[i - 1]

        local_title = newslide_node.attributes["localtitle"].strip()
        title = check_section.children[0].astext().strip()
        if local_title and local_title.startswith("+"):
            title = f"{title} {local_title[1:]}"
        elif local_title:
            title = local_title

        new_section = nodes.section("")
        new_section.attributes = newslide_node.attributes
        doctree.set_id(new_section)

        new_section += nodes.title("", title)

        for next_node in parent_section[
            parent_section.index(newslide_node) + 1 :
        ]:
            new_section.append(next_node.deepcopy())
            parent_section.remove(next_node)

        chapter = parent_section.parent
        chapter.insert(chapter.index(parent_section) + 1, new_section)
        parent_section.remove(newslide_node)
