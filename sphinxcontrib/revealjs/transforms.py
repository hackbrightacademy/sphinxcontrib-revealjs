"""sphinxcontrib.revealjs.transforms"""

from sphinx.application import Sphinx
from docutils import nodes

from . import addnodes


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


def process_newslides(app: Sphinx, doctree: nodes.document, _) -> None:
    """Process newslides after doctree is resolved."""

    while doctree.traverse(addnodes.newslide):
        newslide_node = doctree.next_node(addnodes.newslide)
        parent_section = newslide_node.parent

        title = ""
        if app.config.revealjs_newslides_inherit_titles:
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
