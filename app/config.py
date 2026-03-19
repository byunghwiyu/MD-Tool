from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

APP_DIR    = BASE_DIR / "app"
WORKSPACE_DIR = BASE_DIR / "workspace"
OUTPUTS_DIR   = BASE_DIR / "outputs"
TEMPLATES_DIR = APP_DIR / "templates"
STATIC_DIR    = APP_DIR / "static"
UPLOADS_DIR   = WORKSPACE_DIR / "uploads"
TEMP_DIR      = WORKSPACE_DIR / "temp"

# MD Export
AVAILABLE_TEMPLATES = ["clean-report", "technical-docs", "print-essay"]
DEFAULT_TEMPLATE    = "clean-report"

# addon: 번역 (활성화 시 True)
TRANSLATION_ENABLED = False

# PDF → MD (marker_single 경로)
import os
MARKER_PATH = Path(
    os.environ.get(
        "MARKER_SINGLE_PATH",
        r"C:\Users\Yu\AppData\Roaming\Python\Python310\Scripts\marker_single.exe",
    )
)
