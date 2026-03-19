import json
import re
from datetime import datetime
from pathlib import Path as _Path
from pathlib import Path
from app.config import OUTPUTS_DIR


def make_stem(filename: str) -> str:
    """원본 파일명에서 안전한 폴더/파일명용 stem 추출"""
    raw = _Path(filename).stem
    clean = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', raw).strip()
    return clean[:80] or "document"


def save_export_output(
    job_id: str,
    source_md: str,
    preview_html: str,
    metadata: dict,
    translated_md: str | None = None,
) -> Path:
    stem = make_stem(metadata.get("source_filename") or "document")
    job_dir = OUTPUTS_DIR / f"{stem}_{job_id}"
    job_dir.mkdir(parents=True, exist_ok=True)

    (job_dir / "source.md").write_text(source_md, encoding="utf-8")
    (job_dir / f"{stem}.html").write_text(preview_html, encoding="utf-8")

    if translated_md is not None:
        (job_dir / "translated.md").write_text(translated_md, encoding="utf-8")

    meta = {
        "type": "export",
        "job_id": job_id,
        "created_at": datetime.now().isoformat(),
        "template": metadata.get("template"),
        "source_filename": metadata.get("source_filename"),
        "stem": stem,
        "translation": metadata.get("translation", None),
    }
    (job_dir / "metadata.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return job_dir


# addon: 번역 결과 저장 (TRANSLATION_ENABLED 시 사용)
def save_translate_output(
    job_id: str,
    source_text: str,
    translated_text: str,
    metadata: dict,
) -> Path:
    job_dir = OUTPUTS_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    (job_dir / "source.txt").write_text(source_text, encoding="utf-8")
    (job_dir / "translated.txt").write_text(translated_text, encoding="utf-8")

    meta = {
        "type": "translate",
        "job_id": job_id,
        "created_at": datetime.now().isoformat(),
        "engine": metadata.get("engine"),
        "source_lang": metadata.get("source_lang"),
        "target_lang": metadata.get("target_lang"),
        "source_filename": metadata.get("source_filename"),
    }
    (job_dir / "metadata.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return job_dir
