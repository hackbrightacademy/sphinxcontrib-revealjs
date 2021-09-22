import sys
from pathlib import Path


sys.path.append(
    str((Path(__file__).parent / Path("../sphinxcontrib")).resolve())
)

extensions = ["revealjs"]
html_sidebars = {"**": []}
html_domain_indices = False
html_use_index = False
exclude_patterns = ["env", "_build"]
revealjs_theme_options = {"revealjs_theme": "solarized.css"}
