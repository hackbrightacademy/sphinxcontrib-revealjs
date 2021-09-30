"""sphinxcontrib.revealjs.soupbridge"""

from typing import Callable
from bs4.element import Tag
from bs4 import BeautifulSoup


HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}


class SoupBridge:
    """A bridge to BeautifulSoup-related operations."""

    def __init__(self, filename: str, parser: str = "html.parser"):
        self.filename = filename

        with open(self.filename) as f:
            self.soup = BeautifulSoup(f.read(), parser)

    def write(self):
        with open(self.filename, "w") as f:
            f.write(self.soup.prettify())

    def get_tag_depth(
        self, tag: Tag, stopwhen: Callable[[Tag], bool] = None
    ) -> int:
        """Get the depth of `tag`.

        By default, this will traverse up until it gets to the
        root node. You can also stop when a condition is `True`
        by passing in a value for `stopwhen`.
        """

        depth = 0
        curr = tag
        while curr:
            if stopwhen and stopwhen(curr):
                break

            depth += 1
            curr = curr.parent

        return depth

    def copy_tag(self, tag: Tag, children: bool = False) -> Tag:
        """Return a copy of `tag`.

        This only copies the tag's name and attributes by default,
        so the returned tag won't have any children.

        Children aren't deep-copied. They're shallow-copied. Why?
        Because I said so :D
        """

        copied_tag = self.soup.new_tag(tag.name, **tag.attrs)

        if children:
            for child in tag.contents:
                copied_tag.append(child)

        return copied_tag
