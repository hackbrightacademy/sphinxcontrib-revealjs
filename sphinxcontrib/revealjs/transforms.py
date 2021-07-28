"""sphinxcontrib.revealjs.transforms"""

from pydoc import doc
from sphinx.application import Sphinx
from docutils.nodes import document, Node

from docutils import nodes

from .addnodes import newslide


def get_section_depth(section: nodes.section) -> int:
    depth = 0

    curr = section
    while curr.parent:
        depth += 1
        curr = curr.parent

    return depth or 1


def mark_section_depth(doctree: document):
    for section in doctree.traverse(nodes.section):
        depth = get_section_depth(section)

        section["depth"] = depth
        section[0]["depth"] = depth


def make_title_slide(section: nodes.section):
    title, rest = section.children[0], section.children[1:]

    title_section = nodes.section("", title, ids=section.get("ids", []))

    section.children = []
    section["ids"] = []
    section.append(title_section)
    section.extend(rest)


def doctree_read(app: Sphinx, doctree: document):
    mark_section_depth(doctree)
    make_title_slide(doctree[0])
    for section in doctree.traverse(nodes.section):
        if (
            app.env.config.revealjs_vertical_slides
            and "depth" in section
            and section["depth"] == 2
        ):
            make_title_slide(section)

    # Remove extra nested section. Whoops
    doctree.children = doctree[0].children


def migrate_transitions_to_newslides(
    app: Sphinx, doctree: nodes.document
) -> None:
    for node in doctree.traverse(nodes.transition):
        node.replace_self(newslide("", localtitle=""))


def process_newslides(app: Sphinx, doctree, fromdocname: str) -> None:
    """Process newslides after doctree is resolved."""

    while doctree.traverse(newslide):
        newslide_node = doctree.next_node(newslide)
        if app.builder.name != "revealjs":
            newslide_node.parent.remove(newslide_node)
            continue

        new_section = nodes.section("")
        new_section.attributes = newslide_node.attributes
        doctree.set_id(new_section)

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

        if not isinstance(
            newslide_node.next_node(siblings=True), nodes.section
        ):
            titlenode = nodes.title("", title)
            new_section += titlenode

        for next_node in parent_section[
            parent_section.index(newslide_node) + 1 :
        ]:
            new_section.append(next_node.deepcopy())
            parent_section.remove(next_node)

        chapter = parent_section.parent
        chapter.insert(chapter.index(parent_section) + 1, new_section)
        parent_section.remove(newslide_node)
