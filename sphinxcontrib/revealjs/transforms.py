"""sphinxcontrib.revealjs.transforms"""

from sphinx.application import Sphinx
from docutils import nodes

from .addnodes import newslide


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
        node.replace_self(newslide("", localtitle=""))
