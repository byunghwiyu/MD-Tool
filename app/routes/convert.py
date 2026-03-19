import shutil
import subprocess
import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.config import MARKER_PATH, OUTPUTS_DIR, UPLOADS_DIR
from app.services.job_store import job_store
from app.services.pdf_to_md_runner import estimate_duration, run_marker
from app.services.result_writer import make_stem

router = APIRouter(prefix="/convert")


def _sanitize(name: str) -> str:
    cleaned = "".join(
        ch for ch in name if ch.isalnum() or ch in (" ", ".", "_", "-", "(", ")")
    ).strip()
    return cleaned or "document.pdf"


@router.get("/health")
def convert_health():
    return {
        "marker_exists": MARKER_PATH.exists(),
        "marker_path": str(MARKER_PATH),
    }


@router.get("/jobs")
def list_convert_jobs():
    return {"jobs": job_store.list()[:30]}


@router.get("/jobs/{job_id}")
def get_convert_job(job_id: str):
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다.")
    return job


@router.post("/jobs")
async def create_convert_job(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    output_format: str = Form("markdown"),
    page_range: str = Form(""),
    force_ocr: bool = Form(False),
):
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="PDF 파일만 업로드 가능합니다.")

    safe_name = _sanitize(file.filename or "document.pdf")
    stem = make_stem(safe_name)
    job_id = uuid.uuid4().hex[:12]

    upload_path = UPLOADS_DIR / f"{job_id}-{safe_name}"
    output_dir = OUTPUTS_DIR / f"{stem}_{job_id}"
    output_dir.mkdir(parents=True, exist_ok=True)

    with upload_path.open("wb") as buf:
        shutil.copyfileobj(file.file, buf)

    file_size = upload_path.stat().st_size
    estimated = estimate_duration(file_size)

    job = job_store.create({
        "id": job_id,
        "type": "convert",
        "filename": safe_name,
        "status": "queued",
        "created_at": job_store.utc_now(),
        "started_at": None,
        "finished_at": None,
        "error": None,
        "options": {"output_format": output_format, "page_range": page_range, "force_ocr": force_ocr},
        "input_path": str(upload_path),
        "output_dir": str(output_dir),
        "file_size": file_size,
        "estimated_seconds": estimated,
        "elapsed_seconds": 0,
        "eta_seconds": estimated,
        "progress": 5,
        "files": [],
        "preview": "",
        "preview_type": "text",
        "log": "",
        "command": [],
    })

    background_tasks.add_task(
        run_marker, job_id, upload_path, output_dir,
        output_format, page_range.strip() or None, force_ocr,
    )
    return job


@router.get("/jobs/{job_id}/download")
def download_file(job_id: str, path: str):
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다.")
    output_dir = Path(job["output_dir"])
    file_path = (output_dir / path).resolve()
    root = output_dir.resolve()
    if root not in file_path.parents and file_path != root:
        raise HTTPException(status_code=400, detail="잘못된 경로입니다.")
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")
    return FileResponse(file_path, filename=file_path.name)


@router.post("/jobs/{job_id}/open-folder")
def open_convert_folder(job_id: str):
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다.")
    output_dir = Path(job["output_dir"])
    if not output_dir.exists():
        raise HTTPException(status_code=404, detail="출력 폴더가 없습니다.")
    subprocess.Popen(["explorer.exe", str(output_dir)])
    return {"ok": True}
