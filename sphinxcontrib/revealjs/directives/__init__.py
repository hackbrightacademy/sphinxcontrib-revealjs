"""sphinxcontrib.revealjs.directives"""

from typing import Optional

from docutils.parsers.rst import directives

import xml.dom
import cssutils


def optional_csscolorvalue(argument: Optional[str]) -> Optional[str]:
    """Check for valid CSS color value; raise ``ValueError`` if not."""

    if argument is None:
        return None
    else:
        try:
            color = cssutils.css.ColorValue(argument)
        except xml.dom.SyntaxErr:
            raise ValueError(f"{argument} is not a valid CSS color.")

        return color.cssText


def optional_uri(argument: Optional[str]) -> Optional[str]:
    """Return URI with unescaped whitespace removed or ``None``."""

    if argument is None:
        return None
    else:
        return directives.uri(argument)
