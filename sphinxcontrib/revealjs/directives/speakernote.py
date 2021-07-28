from typing import List
from docutils import nodes

from sphinx.util.docutils import SphinxDirective

from ..addnodes import speakernote


class Speakernote(SphinxDirective):
    has_content = True

    def run(self) -> List[nodes.Node]:
        self.assert_has_content()
        node = speakernote("\n".join(self.content))
        node["classes"] += ["notes"]
        self.add_name(node)
        self.state.nested_parse(self.content, self.content_offset, node)
        return [node]
