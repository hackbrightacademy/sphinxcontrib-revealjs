"""sphinxcontrib.revealjs.transforms"""

from pydoc import doc
from sphinx.application import Sphinx
from docutils.nodes import document, Node

from docutils import nodes


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

    # import pdb

    # pdb.set_trace()
    # sections = list(doctree.traverse(nodes.section))


def setup(app: Sphinx):
    app.connect("doctree-read", doctree_read)
    app.add_config_value("revealjs_vertical_slides", True, "html")
