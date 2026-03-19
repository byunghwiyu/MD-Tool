from pygments.formatters import HtmlFormatter
from app.config import TEMPLATES_DIR

_HIGHLIGHT_STYLE = {
    "clean-report":   "friendly",
    "technical-docs": "monokai",
    "print-essay":    "friendly",
}


def build_html(content_html: str, template_name: str, title: str = "Document") -> str:
    base_template = (TEMPLATES_DIR / "base.html").read_text(encoding="utf-8")
    css_path = TEMPLATES_DIR / f"{template_name}.css"
    template_css = css_path.read_text(encoding="utf-8") if css_path.exists() else ""
    highlight_css = HtmlFormatter(
        style=_HIGHLIGHT_STYLE.get(template_name, "friendly")
    ).get_style_defs(".codehilite")

    return (
        base_template
        .replace("{{ title }}", title)
        .replace("{{ css }}", highlight_css + "\n\n" + template_css)
        .replace("{{ content }}", content_html)
    )
