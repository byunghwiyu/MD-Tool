import re
import markdown

MARKDOWN_EXTENSIONS = [
    "tables",
    "fenced_code",
    "codehilite",
    "toc",
    "nl2br",
    "sane_lists",
]

_CITATION_PATTERN = re.compile(r'\[\s*cite\w+\d*\s*\]|\bcite\w+\d+\w*\b')


def _clean(md_text: str) -> str:
    return _CITATION_PATTERN.sub('', md_text)


def render_markdown(md_text: str) -> str:
    return markdown.markdown(_clean(md_text), extensions=MARKDOWN_EXTENSIONS)
