import uuid
import subprocess
import sys
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel

from app.config import AVAILABLE_TEMPLATES, DEFAULT_TEMPLATE, OUTPUTS_DIR
from app.services.job_runner import run_export_job

router = APIRouter()


class TranslationOptions(BaseModel):
    """addon: 번역 옵션 (TRANSLATION_ENABLED 시 사용)"""
    engine: str
    source_lang: str
    target_lang: str


@router.post("/export")
async def export_markdown(
    file: UploadFile = File(...),
    template: str = Form(DEFAULT_TEMPLATE),
):
    if not file.filename.endswith(".md"):
        raise HTTPException(status_code=400, detail="마크다운 파일(.md)만 업로드 가능합니다.")
    if template not in AVAILABLE_TEMPLATES:
        raise HTTPException(status_code=400, detail=f"지원하지 않는 템플릿: {template}")

    md_text = (await file.read()).decode("utf-8")
    job_id  = str(uuid.uuid4())[:8]

    return run_export_job(
        job_id=job_id,
        md_text=md_text,
        template_name=template,
        source_filename=file.filename,
        translation_options=None,
    )


def _find_export_dir(job_id: str):
    """job_id로 끝나는 outputs 하위 폴더 탐색"""
    if OUTPUTS_DIR.exists():
        for d in OUTPUTS_DIR.iterdir():
            if d.is_dir() and d.name.endswith(f"_{job_id}"):
                return d
    return None


@router.get("/open-folder/{job_id}")
def open_folder(job_id: str):
    job_dir = _find_export_dir(job_id)
    if not job_dir or not job_dir.exists():
        raise HTTPException(status_code=404, detail="작업 폴더를 찾을 수 없습니다.")
    if sys.platform == "win32":
        subprocess.Popen(["explorer", str(job_dir)])
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(job_dir)])
    else:
        subprocess.Popen(["xdg-open", str(job_dir)])
    return {"status": "ok"}
